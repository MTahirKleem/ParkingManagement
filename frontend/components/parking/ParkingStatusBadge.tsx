import { Badge } from "@/components/ui/badge";
import type { ParkingStatus } from "@/types/parking";

export function ParkingStatusBadge({ status }: { status: ParkingStatus }) {
  const variant =
    status === "active"
      ? "default"
      : status === "completed"
        ? "secondary"
        : status === "deleted"
          ? "destructive"
          : "outline";
  return (
    <Badge className="capitalize" variant={variant}>
      {status}
    </Badge>
  );
}
