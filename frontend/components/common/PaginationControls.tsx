import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";

export function PaginationControls({
  page,
  pages,
  total,
  onPageChange,
}: {
  page: number;
  pages: number;
  total: number;
  onPageChange: (page: number) => void;
}) {
  return (
    <div className="flex flex-col gap-3 border-t px-4 py-3 text-sm sm:flex-row sm:items-center sm:justify-between">
      <p className="text-muted-foreground">
        {total} {total === 1 ? "record" : "records"}
      </p>
      <div className="flex items-center gap-2">
        <Button
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          size="sm"
          variant="outline"
        >
          <ChevronLeft />
          Previous
        </Button>
        <span className="min-w-20 text-center text-muted-foreground">
          {page} / {Math.max(pages, 1)}
        </span>
        <Button
          disabled={page >= pages}
          onClick={() => onPageChange(page + 1)}
          size="sm"
          variant="outline"
        >
          Next
          <ChevronRight />
        </Button>
      </div>
    </div>
  );
}
