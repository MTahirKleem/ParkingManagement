import { PageHeader } from "@/components/common/PageHeader";
import { ParkingSearchForm } from "@/components/parking/ParkingSearchForm";

export default function ParkingSearchPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Parking"
        title="Search parking"
        description="Search active and completed records using any common plate format."
      />
      <ParkingSearchForm />
    </div>
  );
}
