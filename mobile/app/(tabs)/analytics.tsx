import { useQuery } from "@tanstack/react-query";
import { View, Text, StyleSheet, ScrollView, Pressable } from "react-native";
import { api } from "@/services/api";
import { useState } from "react";

function Bar({ label, value, max }: { label: string; value: number; max: number }) {
  const pct = max ? (value / max) * 100 : 0;
  return (
    <View style={styles.barRow}>
      <Text style={styles.barLabel}>{label}</Text>
      <View style={styles.barTrack}>
        <View style={[styles.barFill, { width: `${Math.min(100, pct)}%` }]} />
      </View>
      <Text style={styles.barAmount}>{value.toFixed(2)}</Text>
    </View>
  );
}

export default function Analytics() {
  const [mode, setMode] = useState<"monthly" | "yearly">("monthly");
  const { data, isLoading } = useQuery({ queryKey: ["analytics", mode], queryFn: () => (mode === "monthly" ? api.analyticsMonthly() : api.analyticsYearly()) });
  if (isLoading) return <View style={styles.center}><Text>Loading analytics…</Text></View>;
  const items = data?.items ?? [];
  const max = items.reduce((m: number, it: any) => Math.max(m, Number(it.total)), 0);
  return (
    <ScrollView contentContainerStyle={styles.page}>
      <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
        <Text style={styles.title}>{mode === "monthly" ? "Monthly Income" : "Yearly Income"}</Text>
        <View style={{ flexDirection: "row", gap: 8 }}>
          <Pressable onPress={() => setMode("monthly") } style={[styles.toggle, mode === "monthly" && styles.toggleActive]}><Text>Monthly</Text></Pressable>
          <Pressable onPress={() => setMode("yearly") } style={[styles.toggle, mode === "yearly" && styles.toggleActive]}><Text>Yearly</Text></Pressable>
        </View>
      </View>
      {items.map((it: any) => (
        <Bar key={it.period} label={it.period} value={Number(it.total)} max={max} />
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  page: { padding: 20, gap: 12, backgroundColor: "#F8FAFC", flexGrow: 1 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  title: { fontSize: 20, fontWeight: "700", marginBottom: 8 },
  toggle: { padding: 8, borderRadius: 8, backgroundColor: "#F1F5F9" },
  toggleActive: { backgroundColor: "#D1FAE5" },
  barRow: { flexDirection: "row", alignItems: "center", gap: 8 },
  barLabel: { width: 80, color: "#475569" },
  barTrack: { flex: 1, height: 18, backgroundColor: "#E2E8F0", borderRadius: 8, overflow: "hidden" },
  barFill: { height: 18, backgroundColor: "#0F766E" },
  barAmount: { width: 80, textAlign: "right", color: "#0F172A" },
});
