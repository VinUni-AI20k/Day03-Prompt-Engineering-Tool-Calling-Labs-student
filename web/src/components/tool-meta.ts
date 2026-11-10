import {
  BookOpen,
  Clock,
  FileDown,
  FileText,
  Globe,
  Hash,
  LayoutList,
  MessageCircleQuestionMark,
  Send,
  ShieldCheck,
  Sigma,
  Wrench,
  type LucideIcon,
} from "lucide-react";

type Meta = { label: string; icon: LucideIcon };

const META: Record<string, Meta> = {
  clarify: { label: "Hỏi lại", icon: MessageCircleQuestionMark },
  timeline: { label: "Bài đăng của một tài khoản", icon: Clock },
  social_search: { label: "Tìm trên mạng xã hội", icon: Hash },
  lookup: { label: "Tra cứu web", icon: Globe },
  fetch: { label: "Đọc nội dung link", icon: FileDown },
  format: { label: "Định dạng bản tin", icon: LayoutList },
  send: { label: "Gửi Telegram", icon: Send },
  policy: { label: "Tra chính sách", icon: ShieldCheck },
  papers: { label: "Tìm bài báo", icon: BookOpen },
  paper_text: { label: "Đọc bài báo", icon: FileText },
  stats: { label: "Thống kê", icon: Sigma },
};

export function toolMeta(name: string): Meta {
  return META[name] ?? { label: name, icon: Wrench };
}
