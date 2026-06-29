import { PageHeader } from "@/components/common/PageHeader";
import { ParkingHistoryTable } from "@/components/parking/ParkingHistoryTable";

export default function ParkingHistoryPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Parking"
        title="Parking history"
        description="Review active, completed, and cancelled parking records."
      />
      <ParkingHistoryTable />
    </div>
  );
}
