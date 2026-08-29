"use client";

import { useEffect, useState } from "react";
import { Search, ShieldCheck, ShieldOff } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAccounts } from "@/hooks/use-accounts";
import { useDebounced } from "@/hooks/use-debounce";
import { api, errorMessage } from "@/lib/api";
import { formatDate } from "@/lib/format";
import { useAuth } from "@/store/auth";

const ALL = "all";

const ROLE_ITEMS = {
  [ALL]: "All roles",
  ADMIN: "Admin",
  HR: "HR",
  MANAGER: "Manager",
  EMPLOYEE: "Employee",
};

const VERIFIED_ITEMS = {
  [ALL]: "All accounts",
  false: "Waiting for verification",
  true: "Verified",
};

export default function AccountsPage() {
  const me = useAuth((s) => s.user);

  const [searchInput, setSearchInput] = useState("");
  const [role, setRole] = useState(ALL);
  const [verified, setVerified] = useState(ALL);
  const [acting, setActing] = useState<string | null>(null);

  const search = useDebounced(searchInput);

  const { data, loading, error, refresh } = useAccounts({
    search,
    role: role === ALL ? "" : role,
    verified: verified === ALL ? "" : verified,
  });

  async function toggle(user: { id: string; is_verified: boolean; email: string }) {
    setActing(user.id);
    try {
      const path = user.is_verified ? "unverify" : "verify";
      await api.post(`/auth/users/${user.id}/${path}/`, {});
      toast.success(
        user.is_verified
          ? `${user.email} can no longer sign in.`
          : `${user.email} can now sign in.`,
      );
      refresh();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setActing(null);
    }
  }

  const waiting = data?.results.filter((u) => !u.is_verified).length ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Accounts</h1>
        <p className="text-sm text-muted-foreground">
          {loading
            ? "Loading…"
            : `${data?.count ?? 0} accounts${
                waiting ? ` · ${waiting} on this page waiting for verification` : ""
              }`}
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative min-w-56 flex-1">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search name or email"
            className="pl-9"
          />
        </div>

        <Select
          items={ROLE_ITEMS}
          value={role}
          onValueChange={(v) => setRole(String(v))}
        >
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Role" />
          </SelectTrigger>
          <SelectContent>
            {Object.entries(ROLE_ITEMS).map(([value, label]) => (
              <SelectItem key={value} value={value}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          items={VERIFIED_ITEMS}
          value={verified}
          onValueChange={(v) => setVerified(String(v))}
        >
          <SelectTrigger className="w-52">
            <SelectValue placeholder="Verification" />
          </SelectTrigger>
          <SelectContent>
            {Object.entries(VERIFIED_ITEMS).map(([value, label]) => (
              <SelectItem key={value} value={value}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Card>
        <CardContent className="p-0">
          {error && <p className="p-6 text-sm text-destructive">{error}</p>}

          {loading && (
            <div className="space-y-2 p-6">
              {Array.from({ length: 6 }).map((_, index) => (
                <Skeleton key={index} className="h-8 w-full" />
              ))}
            </div>
          )}

          {!loading && !error && data?.results.length === 0 && (
            <p className="p-6 text-sm text-muted-foreground">
              No accounts match those filters.
            </p>
          )}

          {!loading && !error && (data?.results.length ?? 0) > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Email</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Joined</TableHead>
                  <TableHead>Access</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                {data!.results.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">{user.email}</TableCell>
                    <TableCell>{user.full_name || "—"}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{user.role}</Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {formatDate(user.date_joined)}
                    </TableCell>
                    <TableCell>
                      {user.is_verified ? (
                        <span className="inline-flex items-center gap-1.5 text-sm">
                          <ShieldCheck className="size-4 text-emerald-600" />
                          Verified
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 text-sm text-amber-600">
                          <ShieldOff className="size-4" />
                          Locked
                        </span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      {/* No button for yourself. The backend refuses it too,
                          but an admin who locks themselves out — and is the
                          only admin — leaves nobody able to undo it. */}
                      {user.id === me?.id ? (
                        <span className="text-xs text-muted-foreground">you</span>
                      ) : (
                        <Button
                          size="sm"
                          variant={user.is_verified ? "outline" : "default"}
                          loading={acting === user.id}
                          onClick={() => toggle(user)}
                        >
                          {user.is_verified ? "Revoke" : "Verify"}
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
