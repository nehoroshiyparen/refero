import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Header } from "@/shared/ui/header";
import { Button } from "@/shared/ui/button";
import { getReviewAssignments } from "@/entities/review";
import type { ReviewAssignmentFullPayload } from "@/entities/review/types";

const statusColors: Record<string, string> = {
  APPROVED: "text-green-600",
  REJECTED: "text-red-600",
  REQUESTING_CHANGES: "text-amber-600",
};

const statusLabels: Record<string, string> = {
  APPROVED: "Одобрена",
  REJECTED: "Отклонена",
  REQUESTING_CHANGES: "Запрошены изменения",
};

type FilterStatus = "all" | "pending" | "APPROVED" | "REJECTED" | "REQUESTING_CHANGES";

const filterOptions: { value: FilterStatus; label: string }[] = [
  { value: "all", label: "Все" },
  { value: "pending", label: "Ожидают" },
  { value: "APPROVED", label: "Одобрена" },
  { value: "REJECTED", label: "Отклонена" },
  { value: "REQUESTING_CHANGES", label: "Запрошены изменения" },
];

export function AssignmentsPage() {
  const navigate = useNavigate();

  const [assignments, setAssignments] = useState<ReviewAssignmentFullPayload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState<FilterStatus>("all");

  useEffect(() => {
    getReviewAssignments()
      .then(setAssignments)
      .catch((e: any) => setError(e.message ?? "Ошибка загрузки"))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    let result = assignments;

    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter(
        (a) =>
          (a.article_title ?? "").toLowerCase().includes(q) ||
          (a.version_title ?? "").toLowerCase().includes(q),
      );
    }

    if (filterStatus !== "all") {
      if (filterStatus === "pending") {
        result = result.filter((a) => a.review_status === null);
      } else {
        result = result.filter((a) => a.review_status === filterStatus);
      }
    }

    return result;
  }, [assignments, search, filterStatus]);

  if (loading) {
    return (
      <div className="min-h-svh flex flex-col">
        <Header />
        <div className="flex-1 flex items-center justify-center text-muted-foreground">
          Загрузка...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-svh flex flex-col">
        <Header />
        <div className="flex-1 flex flex-col items-center justify-center gap-4">
          <p className="text-destructive">{error}</p>
          <Button variant="outline" onClick={() => navigate("/")}>
            На главную
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-svh flex flex-col">
      <Header />
      <div className="flex-1 max-w-4xl w-full mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold tracking-tight mb-6">Мои рецензии</h1>

        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 mb-6">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Поиск по названию..."
            className="flex-1 rounded-lg border px-3 py-2 text-sm w-full sm:w-auto"
          />
          <div className="flex items-center gap-1 flex-wrap">
            {filterOptions.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setFilterStatus(opt.value)}
                className={`rounded-full px-3 py-1 text-xs border transition-colors ${
                  filterStatus === opt.value
                    ? "border-primary bg-primary/10 text-primary font-medium"
                    : "border-border text-muted-foreground hover:border-foreground"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {filtered.length === 0 ? (
          <p className="text-muted-foreground">
            {assignments.length === 0 ? "Нет назначений" : "Ничего не найдено"}
          </p>
        ) : (
          <div className="space-y-3">
            {filtered.map((a) => (
              <div
                key={a.id}
                className="rounded-xl border p-4 flex items-center justify-between cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => navigate(`/reviews/assignments/${a.id}`)}
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">
                    {a.article_title || "Без названия"}
                  </p>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    Версия {a.version_number}
                    {a.version_title && <> &mdash; {a.version_title}</>}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Назначена{" "}
                    {new Date(a.created_at).toLocaleDateString("ru-RU")}
                  </p>
                </div>
                <div className="ml-4 shrink-0">
                  {a.review_status ? (
                    <span
                      className={`text-sm font-medium ${statusColors[a.review_status] || ""}`}
                    >
                      {statusLabels[a.review_status] || a.review_status}
                    </span>
                  ) : (
                    <span className="text-sm text-muted-foreground">
                      Ожидает
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
