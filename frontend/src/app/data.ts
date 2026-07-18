import type { BotStatus, View } from "./core/types";

export const applicationData = [
  { day: "Mon", sent: 12, responses: 2 },
  { day: "Tue", sent: 18, responses: 4 },
  { day: "Wed", sent: 9, responses: 1 },
  { day: "Thu", sent: 22, responses: 5 },
  { day: "Fri", sent: 15, responses: 3 },
  { day: "Sat", sent: 7, responses: 2 },
  { day: "Sun", sent: 4, responses: 1 },
];

export const platformData = [
  { platform: "LinkedIn", applied: 54, responses: 8 },
  { platform: "Indeed", applied: 31, responses: 4 },
  { platform: "Glassdoor", applied: 19, responses: 2 },
  { platform: "Dice", applied: 12, responses: 3 },
];

export const funnelData = [
  { name: "Applied", value: 116, color: "#10b981" },
  { name: "Viewed", value: 43, color: "#3b82f6" },
  { name: "Responded", value: 17, color: "#f59e0b" },
  { name: "Interview", value: 5, color: "#8b5cf6" },
];

export const recentActivity = [
  {
    id: 1,
    role: "Senior Python Developer",
    company: "Stripe",
    platform: "LinkedIn",
    time: "2 min ago",
    status: "sent",
  },
  {
    id: 2,
    role: "Backend Engineer",
    company: "Notion",
    platform: "Indeed",
    time: "8 min ago",
    status: "viewed",
  },
  {
    id: 3,
    role: "ML Engineer",
    company: "Hugging Face",
    platform: "LinkedIn",
    time: "14 min ago",
    status: "sent",
  },
  {
    id: 4,
    role: "Software Engineer II",
    company: "Figma",
    platform: "Glassdoor",
    time: "21 min ago",
    status: "responded",
  },
  {
    id: 5,
    role: "Python Backend Dev",
    company: "Vercel",
    platform: "Dice",
    time: "35 min ago",
    status: "sent",
  },
];

export const savedKeywords = [
  "Python",
  "Django",
  "FastAPI",
  "Backend Engineer",
  "ML Engineer",
  "Remote",
];

export const excludedKeywords = ["C++", "Java", "iOS", "Android", "Embedded"];

export const coverLetterTemplates = [
  { id: 1, name: "General Tech Role", lastEdited: "Jun 28, 2026" },
  { id: 2, name: "ML / AI Position", lastEdited: "Jul 1, 2026" },
  { id: 3, name: "Startup Culture Fit", lastEdited: "Jun 15, 2026" },
];

export const statusColors: Record<BotStatus, string> = {
  running: "bg-emerald-500",
  paused: "bg-amber-400",
  stopped: "bg-zinc-400",
};

export const statusLabels: Record<BotStatus, string> = {
  running: "Running",
  paused: "Paused",
  stopped: "Stopped",
};

export const viewTitles: Record<View, string> = {
  dashboard: "Dashboard",
  "bot-control": "Bot Control",
  "saved-info": "Saved Information",
  analytics: "Analytics",
};

export const viewDescriptions: Record<View, string> = {
  dashboard: "Overview of your job application bot activity",
  "bot-control": "Configure and control your automation bot",
  "saved-info": "Manage your profile, resume, and templates",
  analytics: "Detailed metrics and application performance",
};
