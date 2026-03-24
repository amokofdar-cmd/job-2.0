import { useEffect, useState } from "react";
import { getJobs, type Job } from "../api";

export function JobsScreen() {
  const [jobs, setJobs] = useState<Job[]>([]);

  useEffect(() => {
    void getJobs().then(setJobs);
  }, []);

  return (
    <div>
      <h2>Jobs</h2>
      <table>
        <thead>
          <tr>
            <th>Company</th>
            <th>Title</th>
            <th>Tier</th>
            <th>Score</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((j) => (
            <tr key={j.id}>
              <td>{j.company}</td>
              <td>
                <a href={j.url} target="_blank" rel="noreferrer">
                  {j.title}
                </a>
              </td>
              <td>{j.tier}</td>
              <td>{j.score.toFixed(3)}</td>
              <td>{j.applied ? "Applied" : "Pending"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
