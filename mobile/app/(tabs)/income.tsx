import { useQuery } from "@tanstack/react-query";
import { Link } from "expo-router";
import { ActivityIndicator, FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { api } from "@/services/api";

export default function IncomeHistory() {
  const { data, isLoading } = useQuery({ queryKey: ["income"], queryFn: api.income });
  if (isLoading) return <View style={styles.center}><ActivityIndicator /></View>;
  return <View style={styles.page}><Link href="/income/add" asChild><Pressable style={styles.button}><Text style={styles.buttonText}>+ Add income</Text></Pressable></Link><FlatList data={data?.items ?? []} keyExtractor={(item) => item.id} ListEmptyComponent={<Text style={styles.empty}>Your journey starts here. Add your first income to begin tracking progress.</Text>} renderItem={({ item }) => <View style={styles.item}><View><Text style={styles.source}>{item.source}</Text><Text style={styles.meta}>{item.transaction_date} · {item.category}</Text></View><Text style={styles.amount}>KSh {Number(item.amount).toLocaleString()}</Text></View>} /> </View>;
}
const styles = StyleSheet.create({ page: { flex: 1, padding: 20, gap: 18, backgroundColor: "#F8FAFC" }, center: { flex: 1, justifyContent: "center", alignItems: "center" }, button: { backgroundColor: "#0F766E", padding: 15, borderRadius: 12, alignItems: "center" }, buttonText: { color: "white", fontWeight: "700" }, item: { backgroundColor: "white", padding: 16, borderRadius: 12, marginBottom: 10, flexDirection: "row", justifyContent: "space-between" }, source: { fontWeight: "700", color: "#0F172A" }, meta: { color: "#64748B", marginTop: 3 }, amount: { fontWeight: "700" }, empty: { textAlign: "center", color: "#475569", marginTop: 50, lineHeight: 22 } });
