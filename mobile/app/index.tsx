import { ActivityIndicator, View } from "react-native";
import { Redirect } from "expo-router";
import { useAuth } from "@/features/auth/AuthProvider";

export default function Index() {
  const { isLoading, isAuthenticated } = useAuth();
  if (isLoading) return <View style={{ flex: 1, justifyContent: "center" }}><ActivityIndicator /></View>;
  return <Redirect href={isAuthenticated ? "/(tabs)" : "/(auth)/login"} />;
}
