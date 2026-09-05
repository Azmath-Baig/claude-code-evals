// Frontend rendering for task state.
// The union below MUST match backend TASK_STATES in backend/tasks_api.py.

export type TaskState = "open" | "in_progress" | "done";

export const STATE_LABEL: Record<TaskState, string> = {
  open: "Open",
  in_progress: "In progress",
  done: "Done",
};

export const STATE_COLOR: Record<TaskState, string> = {
  open: "#3b82f6",
  in_progress: "#f59e0b",
  done: "#10b981",
};

// Which states the user can move a task to from its current state.
// Must mirror backend TRANSITIONS.
export function nextStates(current: TaskState): TaskState[] {
  switch (current) {
    case "open":
      return ["in_progress"];
    case "in_progress":
      return ["done", "open"];
    case "done":
      return [];
  }
}
