import { useMutation } from "@tanstack/react-query";
import { router } from "expo-router";
import { useState } from "react";
import { Alert, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { useAuth } from "@/features/auth/AuthProvider";
import { api } from "@/services/api";

export default function Register() {
  const { signIn } = useAuth();
  const [email, setEmail] = useState(""); const [password, setPassword] = useState("");
  const mutation = useMutation({ mutationFn: () => api.register(email.trim(), password), onSuccess: async ({ access_token }) => { await signIn(access_token); router.replace("/onboarding"); }, onError: (error: Error) => Alert.alert("Couldn’t create account", error.message) });
  return <View style={styles.page}><Text style={styles.title}>Start your journey</Text><Text style={styles.subtitle}>Your benchmark is editable and your income stays private.</Text><TextInput accessibilityLabel="Email" autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={setEmail} placeholder="you@example.com" style={styles.input} /><TextInput accessibilityLabel="Password" secureTextEntry value={password} onChangeText={setPassword} placeholder="At least 8 characters" style={styles.input} /><Pressable onPress={() => mutation.mutate()} disabled={mutation.isPending || password.length < 8} style={styles.button}><Text style={styles.buttonText}>{mutation.isPending ? "Creating…" : "Create account"}</Text></Pressable></View>;
}
const styles = StyleSheet.create({ page: { flex: 1, justifyContent: "center", padding: 24, gap: 14, backgroundColor: "#F8FAFC" }, title: { fontSize: 30, fontWeight: "700", color: "#0F172A" }, subtitle: { color: "#475569", marginBottom: 16 }, input: { backgroundColor: "white", borderWidth: 1, borderColor: "#CBD5E1", borderRadius: 10, padding: 14, fontSize: 16 }, button: { backgroundColor: "#0F766E", padding: 16, borderRadius: 12, alignItems: "center" }, buttonText: { color: "white", fontWeight: "700" } });
