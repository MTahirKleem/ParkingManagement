import { PageHeader } from "@/components/common/PageHeader";
import { ActiveVehiclesTable } from "@/components/parking/ActiveVehiclesTable";

export default function ActiveVehiclesPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Parking"
        title="Active vehicles"
        description="Monitor vehicles currently in parking and complete cash-paid exits."
      />
      <ActiveVehiclesTable />
    </div>
  );
}
