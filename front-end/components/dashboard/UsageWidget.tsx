"use client";

import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";
import { useTranslations } from "next-intl";
import { apiMessage } from "@/lib/api";
import { BillingService, type UsageResponse } from "@/lib/client";

/** Shows the user's monthly free-quota usage and prepaid balance. */
export default function UsageWidget() {
  const t = useTranslations("usage");
  const [usage, setUsage] = useState<UsageResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    BillingService.getUsage()
      .then((u) => active && setUsage(u))
      .catch((err) => active && setError(apiMessage(err)));
    return () => {
      active = false;
    };
  }, []);

  if (error) return <div className="field-error">{t("loadError")}</div>;
  if (!usage) return null;

  const fmt = (n: number) => n.toLocaleString();

  const total = usage.pages_used + usage.free_pages_remaining;
  const usedPct = total > 0 ? Math.min(100, Math.round((usage.pages_used / total) * 100)) : 100;
  const nearLimit = usage.free_pages_remaining === 0 || usedPct >= 80;

  return (
    <div className="panel usage-panel">
      <div className="panel-head">
        <div>
          <h3>{t("title")}</h3>
          <div className="sub">
            {t("freeUsed", { used: usage.pages_used, total })}
          </div>
        </div>
        <span className={`sc-ico ${nearLimit ? "am" : ""}`}>
          <Sparkles size={18} />
        </span>
      </div>
      <div className="usage-body">
        <div className="usage-meter">
          <div className="usage-meter-top">
            <div className="lead">
              <b>{fmt(usage.free_pages_remaining)}</b> {t("freeLeftLabel")}
            </div>
            <span className={`usage-pct ${nearLimit ? "am" : ""}`}>{usedPct}%</span>
          </div>
          <div className="usage-bar">
            <i className={nearLimit ? "am" : ""} style={{ width: `${usedPct}%` }} />
          </div>
        </div>
        <div className="usage-tiles">
          <div className="usage-tile">
            <div className="k">{t("balance")}</div>
            <div className="v">
              {fmt(usage.balance_vnd)} <span className="u">₫</span>
            </div>
          </div>
          <div className="usage-tile">
            <div className="k">{t("perPageLabel")}</div>
            <div className="v">
              {fmt(usage.price_per_page_vnd)} <span className="u">₫</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
