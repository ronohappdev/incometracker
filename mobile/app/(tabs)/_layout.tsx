import { Redirect, Tabs, router } from "expo-router";
import { useAuth } from "@/features/auth/AuthProvider";
import { useEffect, useRef } from "react";

export default function TabsLayout() {
  const { isAuthenticated } = useAuth();
  const prevAuthState = useRef<boolean>(isAuthenticated);
  
  useEffect(() => {
    // Only redirect when transitioning from authenticated to not authenticated
    if (prevAuthState.current === true && isAuthenticated === false) {
      router.push("/(auth)/login");
    }
    prevAuthState.current = isAuthenticated;
  }, [isAuthenticated]);
  
  if (!isAuthenticated) return <Redirect href="/(auth)/login" />;
  return (
    <Tabs>
      <Tabs.Screen name="index" options={{ title: "Progress" }} />
      <Tabs.Screen name="income" options={{ title: "Income" }} />
      <Tabs.Screen name="analytics" options={{ title: "Analytics" }} />
      <Tabs.Screen name="settings" options={{ title: "Settings" }} />
    </Tabs>
  );
}
