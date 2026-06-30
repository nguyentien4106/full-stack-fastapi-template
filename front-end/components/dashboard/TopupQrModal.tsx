"use client";

import { useEffect, useRef, useState } from "react";
import { CheckCircle2, RefreshCw, X, XCircle } from "lucide-react";
import { useFormatter, useTranslations } from "next-intl";
import { apiMessage } from "@/lib/api";
import { SepayService } from "@/lib/client";

const POLL_INTERVAL_MS = 3_000;
const TIMEOUT_MS = 10 * 60 * 1_000; // 10 minutes

type Phase = "waiting" | "success" | "failed" | "expired";

interface TopupQrModalProps {
  txnRef: string;
  qrUrl: string;
  amount: number;
  account: string;
  bank: string;
  content: string;
  onClose: () => void;
  onSuccess: () => void;
}

export default function TopupQrModal({
  txnRef,
  qrUrl,
  amount,
  account,
  bank,
  content,
  onClose,
  onSuccess,
}: TopupQrModalProps) {
  const t = useTranslations("billing");
  const tc = useTranslations("common");
  const format = useFormatter();

  const [phase, setPhase] = useState<Phase>("waiting");
  const onSuccessRef = useRef(onSuccess);
  onSuccessRef.current = onSuccess;

  const vnd = (n: number) =>
    format.number(n, { style: "currency", currency: "VND", maximumFractionDigits: 0 });

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  useEffect(() => {
    let active = true;
    const deadline = Date.now() + TIMEOUT_MS;

    const poll = async () => {
      if (!active) return;
      if (Date.now() > deadline) {
        if (active) setPhase("expired");
        return;
      }
      try {
        const res = await SepayService.getStatus({ txnRef });
        if (!active) return;
        if (res.status === "success") {
          setPhase("success");
          onSuccessRef.current();
          return;
        }
        if (res.status === "failed") {
          setPhase("failed");
          return;
        }
      } catch {
        // Transient error — keep polling until the deadline.
      }
      if (active) timer = window.setTimeout(poll, POLL_INTERVAL_MS);
    };

    let timer = window.setTimeout(poll, POLL_INTERVAL_MS);
    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [txnRef]);

  return (
    <div className="modal-overlay" onClick={onClose} role="presentation">
      <div
        className="modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={t("qrTitle")}
      >
        <div className="modal-head">
          <div>
            <div className="modal-title">{t("qrTitle")}</div>
            <div className="modal-sub">{t("qrInstructions")}</div>
          </div>
          <button className="modal-close" onClick={onClose} aria-label={tc("close")}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body" style={{ display: "grid", gap: 16, justifyItems: "center" }}>
          {phase === "success" ? (
            <div className="preview-state" style={{ display: "grid", gap: 8, justifyItems: "center" }}>
              <CheckCircle2 size={48} style={{ color: "var(--ok)" }} />
              <div>{t("qrSuccess")}</div>
            </div>
          ) : phase === "failed" ? (
            <div className="preview-state field-error" style={{ display: "grid", gap: 8, justifyItems: "center" }}>
              <XCircle size={48} />
              <div>{t("status_failed")}</div>
            </div>
          ) : phase === "expired" ? (
            <div className="preview-state" style={{ display: "grid", gap: 8, justifyItems: "center" }}>
              <XCircle size={48} style={{ color: "var(--fg-dim)" }} />
              <div>{t("qrExpired")}</div>
            </div>
          ) : (
            <>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={qrUrl}
                alt={t("qrTitle")}
                width={240}
                height={240}
                style={{ borderRadius: 12, background: "#fff", padding: 8 }}
              />
              <div style={{ display: "inline-flex", alignItems: "center", gap: 8, color: "var(--fg-dim)" }}>
                <RefreshCw size={15} className="spin" /> {t("qrWaiting")}
              </div>
            </>
          )}

          <div style={{ width: "100%", display: "grid", gap: 6, fontSize: 13 }}>
            <Row label={t("bankLabel")} value={bank} />
            <Row label={t("accountLabel")} value={account} mono />
            <Row label={t("amountLabel")} value={vnd(amount)} mono />
            <Row label={t("contentLabel")} value={content} mono />
          </div>
        </div>
      </div>
    </div>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
      <span style={{ color: "var(--fg-dim)" }}>{label}</span>
      <span style={mono ? { fontFamily: "var(--font-mono)" } : undefined}>{value}</span>
    </div>
  );
}
