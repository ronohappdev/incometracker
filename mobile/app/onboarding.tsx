import { useMutation } from "@tanstack/react-query";
import { router } from "expo-router";
import { useState } from "react";
import { Alert, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { api } from "@/services/api";

export default function Onboarding() {
  const [name, setName] = useState("Career Benchmark");
  const [startDate, setStartDate] = useState("2022-01-01");
  const [monthlyIncome, setMonthlyIncome] = useState("50000");
  const mutation = useMutation({
    mutationFn: () => api.updateBenchmark({
      name,
      employment_start_date: startDate,
      monthly_income: monthlyIncome,
      currency: "KES",
    }),
    onSuccess: () => router.replace("/(tabs)"),
    onError: (error: Error) => Alert.alert("Couldn’t save benchmark", error.message),
  });
  return <View style={styles.page}><Text style={styles.title}>Set your benchmark</Text><Text style={styles.subtitle}>Use a neutral name and assumptions you can update later.</Text><Text style={styles.label}>Benchmark name</Text><TextInput accessibilityLabel="Benchmark name" value={name} onChangeText={setName} style={styles.input} /><Text style={styles.label}>Employment start date</Text><TextInput accessibilityLabel="Employment start date" value={startDate} onChangeText={setStartDate} placeholder="YYYY-MM-DD" style={styles.input} /><Text style={styles.label}>Monthly income (KSh)</Text><TextInput accessibilityLabel="Benchmark monthly income" keyboardType="decimal-pad" value={monthlyIncome} onChangeText={setMonthlyIncome} style={styles.input} /><Pressable onPress={() => mutation.mutate()} disabled={mutation.isPending} style={styles.button}><Text style={styles.buttonText}>{mutation.isPending ? "Saving…" : "Continue"}</Text></Pressable></View>;
}
const styles = StyleSheet.create({ page: { flex: 1, justifyContent: "center", padding: 24, gap: 10, backgroundColor: "#F8FAFC" }, title: { fontSize: 30, fontWeight: "700", color: "#0F172A" }, subtitle: { color: "#475569", marginBottom: 14, lineHeight: 20 }, label: { marginTop: 8, fontWeight: "600", color: "#334155" }, input: { backgroundColor: "white", borderWidth: 1, borderColor: "#CBD5E1", borderRadius: 10, padding: 14, fontSize: 16 }, button: { marginTop: 18, backgroundColor: "#0F766E", padding: 16, borderRadius: 12, alignItems: "center" }, buttonText: { color: "white", fontWeight: "700" } });
