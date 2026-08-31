import { useQuery } from "@tanstack/react-query";
import { Link } from "expo-router";
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { api } from "@/services/api";

const kes = (value: string | number) => `KSh ${Number(value).toLocaleString("en-KE", { minimumFractionDigits: 2 })}`;

export default function Dashboard() {
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["dashboard"], queryFn: api.dashboard });
  if (isLoading) return <View style={styles.center}><ActivityIndicator /></View>;
  if (error) return <View style={styles.center}><Text>We couldn’t load your latest progress.</Text><Pressable onPress={() => refetch()}><Text style={styles.link}>Try again</Text></Pressable></View>;
  return <ScrollView contentContainerStyle={styles.page}><Text style={styles.eyebrow}>YOUR FINANCIAL PROGRESS</Text><Text style={styles.title}>A clear view of your momentum.</Text><Card label="MY INCOME" value={kes(data.my_total_income)} /><Card label="BENCHMARK" value={kes(data.benchmark_total)} /><Card label={Number(data.surplus) ? "AHEAD BY" : "CURRENT GAP"} value={kes(Number(data.surplus) || data.gap)} /><View style={styles.progress}><Text>Progress</Text><Text>{Number(data.progress_percentage).toFixed(1)}%</Text><View style={styles.track}><View style={[styles.fill, { width: `${Math.min(100, Number(data.progress_percentage))}%` }]} /></View></View><Text style={styles.muted}>This month: {kes(data.monthly_income)} · Gap reduced: {kes(data.gap_change)}</Text><Link href="/income/add" asChild><Pressable style={styles.button}><Text style={styles.buttonText}>+ Add income</Text></Pressable></Link></ScrollView>;
}
function Card({ label, value }: { label: string; value: string }) { return <View style={styles.card}><Text style={styles.eyebrow}>{label}</Text><Text style={styles.amount}>{value}</Text></View>; }
const styles = StyleSheet.create({ page: { padding: 24, gap: 14, backgroundColor: "#F8FAFC", flexGrow: 1 }, center: { flex: 1, alignItems: "center", justifyContent: "center", gap: 16 }, eyebrow: { fontSize: 12, fontWeight: "700", letterSpacing: 1, color: "#64748B" }, title: { fontSize: 26, fontWeight: "700", marginBottom: 12, color: "#0F172A" }, card: { backgroundColor: "white", borderRadius: 14, padding: 18, gap: 5 }, amount: { fontSize: 24, fontWeight: "700", color: "#0F172A" }, progress: { backgroundColor: "white", padding: 18, borderRadius: 14, gap: 10 }, track: { height: 8, borderRadius: 8, backgroundColor: "#E2E8F0" }, fill: { height: 8, backgroundColor: "#0F766E", borderRadius: 8 }, muted: { color: "#475569", lineHeight: 20 }, button: { backgroundColor: "#0F766E", padding: 16, borderRadius: 12, alignItems: "center", marginTop: 10 }, buttonText: { color: "white", fontWeight: "700" }, link: { color: "#0F766E", fontWeight: "700" } });
