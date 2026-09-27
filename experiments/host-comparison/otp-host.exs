# Requires Elixir >= 1.18 (standard-library JSON); no Hex dependencies.
defmodule HostComparison do
  use GenServer

  def start_link(args), do: GenServer.start_link(__MODULE__, args, name: __MODULE__)
  def emit(value), do: IO.puts(JSON.encode!(value))
  defp now, do: System.monotonic_time(:millisecond)

  @impl true
  def init([directory, bun, worker, active, backlog]) do
    active = String.to_integer(active)
    backlog = String.to_integer(backlog)
    true = active in 1..8 and backlog in 1..64
    File.mkdir!(Path.join(directory, "host.lock"))
    File.write!(Path.join([directory, "host.lock", "pid"]), System.pid())
    path = Path.join(directory, "journal.jsonl")
    rows = if File.exists?(path) do
      bytes = File.read!(path)
      true = byte_size(bytes) <= 4_000_000 and (bytes == "" or String.ends_with?(bytes, "\n"))
      bytes |> String.split("\n", trim: true) |> Enum.map(&JSON.decode!/1) |> Enum.map(fn row -> true = record?(row); row end) |> Map.new(&{&1["job"]["id"], &1})
    else
      %{}
    end
    true = map_size(rows) <= 512
    state = %{directory: directory, bun: bun, worker: worker, limit: active, backlog: backlog, rows: rows, queue: [], active: %{}, stopping: false}
    state = Enum.reduce(rows, state, fn {_id, row}, state ->
      if row["status"] in ["queued", "running"] do
        persist(state, Map.merge(row, %{"status" => if(row["status"] == "queued", do: "cancelled", else: "uncertain"), "reason" => "host_restart"}))
      else
        state
      end
    end)
    Process.send_after(self(), :tick, 5)
    emit(%{event: "ready", host: "otp", pid: String.to_integer(System.pid()), active_limit: active, backlog_limit: backlog})
    {:ok, state}
  end

  defp persist(state, row) do
    {:ok, file} = :file.open(String.to_charlist(Path.join(state.directory, "journal.jsonl")), [:append, :binary, :raw])
    :ok = :file.write(file, JSON.encode!(row) <> "\n")
    :ok = :file.sync(file)
    :ok = :file.close(file)
    emit(Map.put(row, "event", "state"))
    %{state | rows: Map.put(state.rows, row["job"]["id"], row)}
  end

  defp identifier?(v), do: is_binary(v) and Regex.match?(~r/^[a-zA-Z0-9_-]{1,64}$/, v)
  defp fields?(v, keys), do: is_map(v) and Enum.sort(Map.keys(v)) == Enum.sort(keys)
  defp job?(v) do
    fields?(v, ["id", "owner", "delay_ms", "ttl_ms", "fault"]) and identifier?(v["id"]) and identifier?(v["owner"]) and
      Enum.all?(["delay_ms", "ttl_ms"], &(is_integer(v[&1]) and v[&1] in 0..30000)) and v["fault"] in ["none", "before_dispatch", "after_effect", "hold_after_effect"]
  end
  defp record?(row) do
    is_map(row) and Enum.all?(Map.keys(row), &(&1 in ["job", "status", "reason", "queue_ms", "digest"])) and
      job?(row["job"]) and row["status"] in ["queued", "running", "complete", "cancelled", "expired", "uncertain"] and
      is_binary(row["reason"]) and byte_size(row["reason"]) <= 128 and
      (not Map.has_key?(row, "queue_ms") or (is_number(row["queue_ms"]) and row["queue_ms"] >= 0)) and
      (not Map.has_key?(row, "digest") or (is_binary(row["digest"]) and Regex.match?(~r/^sha256:[a-f0-9]{64}$/, row["digest"]))) and
      (row["status"] != "complete" or Map.has_key?(row, "digest"))
  end

  @impl true
  def handle_call({:command, cmd}, _from, state) do
    state = pump(state)
    state = cond do
      fields?(cmd, ["op", "job"]) and cmd["op"] == "submit" and job?(cmd["job"]) ->
        job = cmd["job"]
        cond do
          Map.has_key?(state.rows, job["id"]) -> emit(%{event: "duplicate", id: job["id"], status: state.rows[job["id"]]["status"]}); state
          state.stopping or map_size(state.rows) >= 512 or length(state.queue) >= state.backlog -> emit(%{event: "rejected", id: job["id"], reason: "capacity"}); state
          true ->
            state = persist(state, %{"job" => job, "status" => "queued", "reason" => "accepted"})
            %{state | queue: state.queue ++ [{job, now()}]}
        end
      fields?(cmd, ["op", "id"]) and cmd["op"] == "cancel" and identifier?(cmd["id"]) -> cancel(state, cmd["id"], "cancelled_by_owner")
      fields?(cmd, ["op", "owner"]) and cmd["op"] == "owner_down" and identifier?(cmd["owner"]) ->
        Enum.reduce(state.rows, state, fn {id, row}, state -> if row["job"]["owner"] == cmd["owner"], do: cancel(state, id, "owner_down"), else: state end)
      fields?(cmd, ["op"]) and cmd["op"] == "observe" ->
        emit(%{event: "observation", active: map_size(state.active), queued: length(state.queue), retained: map_size(state.rows), beam_allocated_bytes: :erlang.memory(:total)}); state
      fields?(cmd, ["op"]) and cmd["op"] == "stop" -> stop(state)
      fields?(cmd, ["op"]) and cmd["op"] == "crash_owner" -> Process.exit(self(), :kill)
      true -> emit(%{event: "rejected", reason: "invalid_command"}); state
    end
    {:reply, :ok, pump(state)}
  end

  defp cancel(state, id, reason) do
    case state.rows[id] do
      %{"status" => status} = row when status in ["queued", "running"] ->
        state = persist(state, Map.merge(row, %{"status" => if(status == "queued", do: "cancelled", else: "uncertain"), "reason" => reason}))
        case state.active[id] do
          nil -> :ok
          task -> Process.exit(task.pid, :kill)
        end
        state
      _ -> state
    end
  end

  defp stop(state) do
    state = %{state | stopping: true}
    Enum.reduce(Map.keys(state.rows), state, &cancel(&2, &1, "host_stop"))
  end

  defp pump(state) do
    state = Enum.reduce(state.queue, %{state | queue: []}, fn {job, received}, state ->
      cond do
        state.rows[job["id"]]["status"] != "queued" -> state
        now() - received >= job["ttl_ms"] -> persist(state, %{"job" => job, "status" => "expired", "reason" => "deadline_before_dispatch"})
        true -> %{state | queue: state.queue ++ [{job, received}]}
      end
    end)
    state = dispatch(state)
    if state.stopping and map_size(state.active) == 0 do
      File.rm!(Path.join([state.directory, "host.lock", "pid"]))
      File.rmdir!(Path.join(state.directory, "host.lock"))
      System.halt(0)
    end
    state
  end

  defp dispatch(%{queue: [{job, received} | remaining]} = state) when map_size(state.active) < state.limit and not state.stopping do
    state = persist(state, %{"job" => job, "status" => "running", "reason" => "dispatch_intent", "queue_ms" => now() - received})
    parent = self()
    task = Task.Supervisor.async_nolink(HostTasks, fn ->
      owner = Process.monitor(parent)
      port = Port.open({:spawn_executable, state.bun}, [:binary, :exit_status, :use_stdio, :stderr_to_stdout, {:args, [state.worker, JSON.encode!(job), state.directory]}])
      {:os_pid, pid} = Port.info(port, :os_pid)
      send(parent, {:spawned, job["id"], pid})
      collect(port, "", owner)
    end)
    dispatch(%{state | queue: remaining, active: Map.put(state.active, job["id"], task)})
  end
  defp dispatch(state), do: state

  defp collect(port, bytes, owner) do
    receive do
      {^port, {:data, chunk}} when byte_size(bytes) + byte_size(chunk) <= 16384 -> collect(port, bytes <> chunk, owner)
      {^port, {:data, _}} -> Port.close(port); {:error, "worker_output_limit"}
      {^port, {:exit_status, code}} -> {code, bytes}
      {:DOWN, ^owner, :process, _pid, _reason} -> Port.close(port); {:error, "owner_down"}
    after
      31000 -> Port.close(port); {:error, "worker_timeout"}
    end
  end

  @impl true
  def handle_info(:tick, state) do
    Process.send_after(self(), :tick, 5)
    {:noreply, pump(state)}
  end
  def handle_info({:spawned, id, pid}, state) do
    emit(%{event: "spawn", id: id, pid: pid}); {:noreply, state}
  end
  def handle_info({ref, result}, state) when is_reference(ref) do
    Process.demonitor(ref, [:flush])
    {:noreply, settle(state, ref, result)}
  end
  def handle_info({:DOWN, ref, :process, _pid, reason}, state), do: {:noreply, settle(state, ref, {:error, inspect(reason)})}

  defp settle(state, ref, result) do
    case Enum.find(state.active, fn {_id, task} -> task.ref == ref end) do
      nil -> state
      {id, _task} ->
        state = %{state | active: Map.delete(state.active, id)}
        row = state.rows[id]
        state = if row["status"] == "running" do
          digest = case result do
            {0, bytes} ->
              bytes |> String.split("\n", trim: true) |> Enum.flat_map(fn line ->
                case JSON.decode(line) do
                  {:ok, %{"event" => "result", "digest" => d}} when is_binary(d) -> [d]
                  _ -> []
                end
              end) |> List.last()
            _ -> nil
          end
          if digest do
            persist(state, Map.merge(row, %{"status" => "complete", "reason" => "settled", "digest" => digest}))
          else
            persist(state, Map.merge(row, %{"status" => "uncertain", "reason" => "worker_failed"}))
          end
        else
          state
        end
        pump(state)
    end
  end
end

# GenServer is deliberately temporary: automatic replay after owner death would
# violate the unknown-effect rule. The supervisor owns worker tasks, not retries.
args = System.argv()
{:ok, _} = Supervisor.start_link([
  {Task.Supervisor, name: HostTasks},
  Supervisor.child_spec({HostComparison, args}, restart: :temporary)
], strategy: :one_for_one)
# A failed scheduler is not silently replaced. Explicit recovery must classify
# its durable dispatches before the service accepts more work.
host = Process.whereis(HostComparison)
spawn(fn ->
  ref = Process.monitor(host)
  receive do
    {:DOWN, ^ref, :process, ^host, _reason} -> System.halt(76)
  end
end)
read = fn read, pending ->
  case IO.binread(:stdio, 1) do
    :eof -> GenServer.call(HostComparison, {:command, %{"op" => "stop"}}, :infinity)
    {:error, _} -> System.halt(2)
    "\n" ->
      case JSON.decode(pending) do
        {:ok, cmd} -> GenServer.call(HostComparison, {:command, cmd}, :infinity)
        _ -> HostComparison.emit(%{event: "rejected", reason: "invalid_command"})
      end
      read.(read, "")
    byte when byte_size(pending) < 16384 -> read.(read, pending <> byte)
    _ -> HostComparison.emit(%{event: "rejected", reason: "input_too_large"}); GenServer.call(HostComparison, {:command, %{"op" => "stop"}}, :infinity)
  end
end
read.(read, "")
