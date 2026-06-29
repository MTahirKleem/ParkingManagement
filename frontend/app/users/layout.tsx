import { ProtectedLayout } from "@/components/layout/ProtectedLayout";
import { RoleGuard } from "@/components/layout/RoleGuard";

export default function UsersLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedLayout>
      <RoleGuard allowed={["admin"]}>{children}</RoleGuard>
    </ProtectedLayout>
  );
}
