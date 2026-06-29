import { ParkingRecordDetails } from "@/components/parking/ParkingRecordDetails";

export default async function ParkingRecordPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <ParkingRecordDetails id={id} />;
}
