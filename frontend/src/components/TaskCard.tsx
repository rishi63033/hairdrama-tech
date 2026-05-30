/**
 * TaskCard component
 * Displays a single task with status badge, priority indicator,
 * assignee/creator info, and action buttons.
 */

"use client";

import { useState } from "react";
import { Task } from "@/types";
import { format } from "date-fns";
import EditTaskModal from "./EditTaskModal";

interface TaskCardProps {
  task: Task;
  currentUserId: string;
  onComplete: (id: string) => void;
  onDelete: (id: string) => void;
  onRefresh: () => void;
}

const priorityColors = {
  high: "bg-red-100 text-red-700",
  medium: "bg-yellow-100 text-yellow-700",
  low: "bg-green-100 text-green-700",
};

const statusColors = {
  pending: "bg-gray-100 text-gray-600",
  in_progress: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
};

const statusLabels = {
  pending: "Pending",
  in_progress: "In Progress",
  completed: "Completed",
};

export default function TaskCard({
  task,
  currentUserId,
  onComplete,
  onDelete,
  onRefresh,
}: TaskCardProps) {
  const [showEditModal, setShowEditModal] = useState(false);
  const isCreator = task.creator.id === currentUserId;
  const isAssignee = task.assignee?.id === currentUserId;
  const isCompleted = task.status === "completed";

  return (
    <>
      <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow flex flex-col gap-3">
        {/* Header row: status + priority badges */}
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${statusColors[task.status]}`}>
            {statusLabels[task.status]}
          </span>
          <span className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${priorityColors[task.priority]}`}>
            {task.priority} priority
          </span>
        </div>

        {/* Title */}
        <h3 className={`font-semibold text-gray-900 text-base leading-snug ${isCompleted ? "line-through text-gray-400" : ""}`}>
          {task.title}
        </h3>

        {/* Description */}
        {task.description && (
          <p className="text-sm text-gray-500 line-clamp-2">{task.description}</p>
        )}

        {/* Due date */}
        {task.due_date && (
          <p className="text-xs text-gray-400 flex items-center gap-1">
            <span>📅</span>
            Due {format(new Date(task.due_date), "MMM d, yyyy")}
          </p>
        )}

        {/* Creator / Assignee */}
        <div className="text-xs text-gray-400 space-y-1 border-t pt-3">
          <p>
            <span className="font-medium text-gray-500">Created by:</span>{" "}
            {task.creator.name}
          </p>
          {task.assignee && (
            <p>
              <span className="font-medium text-gray-500">Assigned to:</span>{" "}
              {task.assignee.name}
            </p>
          )}
        </div>

        {/* Action buttons */}
        {!isCompleted && (
          <div className="flex gap-2 flex-wrap pt-1">
            {(isCreator || isAssignee) && (
              <button
                onClick={() => onComplete(task.id)}
                className="flex-1 text-xs bg-green-50 text-green-700 border border-green-200 rounded-lg py-1.5 px-3 hover:bg-green-100 transition-colors"
              >
                ✓ Complete
              </button>
            )}
            {isCreator && (
              <>
                <button
                  onClick={() => setShowEditModal(true)}
                  className="text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded-lg py-1.5 px-3 hover:bg-blue-100 transition-colors"
                >
                  Edit
                </button>
                <button
                  onClick={() => onDelete(task.id)}
                  className="text-xs bg-red-50 text-red-700 border border-red-200 rounded-lg py-1.5 px-3 hover:bg-red-100 transition-colors"
                >
                  Delete
                </button>
              </>
            )}
          </div>
        )}

        {isCompleted && task.completed_at && (
          <p className="text-xs text-green-600 flex items-center gap-1">
            <span>✅</span> Completed {format(new Date(task.completed_at), "MMM d, yyyy")}
          </p>
        )}
      </div>

      {showEditModal && (
        <EditTaskModal
          task={task}
          onClose={() => setShowEditModal(false)}
          onUpdated={() => {
            setShowEditModal(false);
            onRefresh();
          }}
        />
      )}
    </>
  );
}
