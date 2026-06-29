import { PageHeader } from "@/components/common/PageHeader";
import { VehicleEntryForm } from "@/components/parking/VehicleEntryForm";
import { Card, CardContent } from "@/components/ui/card";

export default function VehicleEntryPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Parking"
        title="Vehicle entry"
        description="Add a vehicle to active parking. Plate formatting is normalized by the backend."
      />
      <Card className="max-w-3xl">
        <CardContent>
          <VehicleEntryForm />
        </CardContent>
      </Card>
    </div>
  );
}
