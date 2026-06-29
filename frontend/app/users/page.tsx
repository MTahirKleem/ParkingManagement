import { PageHeader } from "@/components/common/PageHeader";
import { GuardForm } from "@/components/users/GuardForm";
import { GuardsTable } from "@/components/users/GuardsTable";

export default function UsersPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Guard accounts"
        description="Create and manage the staff who operate vehicle entry and exit."
        actions={<GuardForm />}
      />
      <GuardsTable />
    </div>
  );
}
