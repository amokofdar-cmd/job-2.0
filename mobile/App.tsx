import React, { useEffect, useState } from "react";
import { SafeAreaView, StyleSheet, Text, TouchableOpacity, View, FlatList, Linking } from "react-native";
import { StatusBar } from "expo-status-bar";
import { getJobs, getMetrics, runAutopilotOnce, type Job, type Metrics } from "./lib/api";

export default function App() {
  const [view, setView] = useState<"dashboard" | "jobs">("dashboard");
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);

  async function refresh() {
    const [m, j] = await Promise.all([getMetrics(), getJobs()]);
    setMetrics(m);
    setJobs(j);
  }

  useEffect(() => {
    void refresh();
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <Text style={styles.title}>job-2.0 Mobile Console</Text>
      <View style={styles.tabs}>
        <TouchableOpacity style={styles.tab} onPress={() => setView("dashboard")}>
          <Text>Dashboard</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.tab} onPress={() => setView("jobs")}>
          <Text>Jobs</Text>
        </TouchableOpacity>
      </View>

      {view === "dashboard" ? (
        <View>
          <Text>Total Jobs: {metrics?.total_jobs ?? "-"}</Text>
          <Text>Applied: {metrics?.applied_jobs ?? "-"}</Text>
          <Text>Pending: {metrics?.pending_jobs ?? "-"}</Text>
          <Text>Attempts: {metrics?.attempts_total ?? "-"}</Text>
          <Text>Success Rate: {((metrics?.success_rate ?? 0) * 100).toFixed(1)}%</Text>
          <TouchableOpacity
            style={styles.runButton}
            onPress={async () => {
              await runAutopilotOnce();
              await refresh();
            }}
          >
            <Text style={{ color: "white" }}>Run Autopilot</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={jobs}
          keyExtractor={(item) => String(item.id)}
          renderItem={({ item }) => (
            <TouchableOpacity style={styles.jobItem} onPress={() => Linking.openURL(item.url)}>
              <Text style={styles.jobTitle}>{item.title}</Text>
              <Text>{item.company}</Text>
              <Text>
                Tier {item.tier} · {item.applied ? "Applied" : "Pending"}
              </Text>
            </TouchableOpacity>
          )}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#f8fafc" },
  title: { fontSize: 22, fontWeight: "700", marginBottom: 12 },
  tabs: { flexDirection: "row", marginBottom: 12 },
  tab: {
    marginRight: 10,
    borderWidth: 1,
    borderColor: "#d1d5db",
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: "white",
  },
  runButton: {
    marginTop: 12,
    backgroundColor: "#2563eb",
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 14,
    alignSelf: "flex-start",
  },
  jobItem: {
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#e5e7eb",
    borderRadius: 10,
    backgroundColor: "white",
  },
  jobTitle: { fontWeight: "600" },
});
