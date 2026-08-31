import { useMutation, useQueryClient } from "@tanstack/react-query";
import { router } from "expo-router";
import { useState } from "react";
import { Alert, Pressable, StyleSheet, Switch, Text, TextInput, View } from "react-native";
import { api } from "@/services/api";

export default function AddIncome() {
  const client = useQueryClient(); const [amount, setAmount] = useState(""); const [source, setSource] = useState("Freelancing"); const [category, setCategory] = useState("Freelancing"); const [recurring, setRecurring] = useState(false);
  const mutation = useMutation({ mutationFn: api.addIncome, onSuccess: () => { client.invalidateQueries({ queryKey: ["dashboard"] }); client.invalidateQueries({ queryKey: ["income"] }); router.back(); }, onError: (e: Error) => Alert.alert("Couldn’t save income", e.message) });
  const save = () => { if (!Number(amount) || Number(amount) <= 0) return Alert.alert("Enter a valid amount", "Amount must be greater than zero."); mutation.mutate({ amount, source, category, recurring, currency: "KES", transaction_date: new Date().toISOString().slice(0, 10) }); };
  return <View style={styles.page}><Text style={styles.label}>Amount (KSh)</Text><TextInput accessibilityLabel="Income amount" keyboardType="decimal-pad" value={amount} onChangeText={setAmount} placeholder="0.00" style={styles.input} /><Text style={styles.label}>Income source</Text><TextInput accessibilityLabel="Income source" value={source} onChangeText={setSource} style={styles.input} /><Text style={styles.label}>Category</Text><TextInput accessibilityLabel="Income category" value={category} onChangeText={setCategory} style={styles.input} /><View style={styles.switch}><Text>Recurring income</Text><Switch value={recurring} onValueChange={setRecurring} /></View><Pressable accessibilityRole="button" onPress={save} disabled={mutation.isPending} style={styles.button}><Text style={styles.buttonText}>{mutation.isPending ? "Saving…" : "Save income"}</Text></Pressable></View>;
}
const styles = StyleSheet.create({ page: { flex: 1, padding: 24, gap: 10, backgroundColor: "#F8FAFC" }, label: { marginTop: 12, fontWeight: "600", color: "#334155" }, input: { borderWidth: 1, borderColor: "#CBD5E1", borderRadius: 10, backgroundColor: "white", padding: 14, fontSize: 16 }, switch: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: 10 }, button: { marginTop: 20, backgroundColor: "#0F766E", borderRadius: 12, padding: 16, alignItems: "center" }, buttonText: { color: "white", fontWeight: "700" } });
