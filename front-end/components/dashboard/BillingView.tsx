"use client";

import { useCallback, useEffect, useState } from "react";
import { ArrowDownRight, ArrowUpRight, RefreshCw, Wallet } from "lucide-react";
import { useFormatter, useTranslations } from "next-intl";
import { apiMessage } from "@/lib/api";
import {
  SepayService,
  TopupService,
  type CreateSepayPaymentResponse,
  type TopupPackage,
  type TopupTransactionPublic,
  type UserBalancePublic,
} from "@/lib/client";
import { formatDate } from "@/lib/files";
import type { DocStatus } from "@/lib/data";
import TopupQrModal from "./TopupQrModal";

const STATUS_PILL: Record<TopupTransactionPublic["status"], DocStatus> = {
  success: "done",
  pending: "proc",
  failed: "fail",
};

export default function BillingView() {
  const t = useTranslations("billing");
  const tc = useTranslations("common");
  const format = useFormatter();

  const [balance, setBalance] = useState<UserBalancePublic | null>(null);
  const [packages, setPackages] = useState<TopupPackage[]>([]);
  const [transactions, setTransactions] = useState<TopupTransactionPublic[]>([]);
  const [loading, setLoading] = useState(true);
  const [payingId, setPayingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [payment, setPayment] = useState<CreateSepayPaymentResponse | null>(null);

  const refresh = useCallback(
    (signal?: { active: boolean }) =>
      Promise.all([
        TopupService.getMyBalance(),
        TopupService.getTopupPackages(),
        TopupService.getMyTransactions({ limit: 20 }),
      ])
        .then(([bal, pkgs, txns]) => {
          if (signal && !signal.active) return;
          setBalance(bal);
          setPackages(pkgs.packages);
          setTransactions(txns);
        })
        .catch((err) => (!signal || signal.active) && setError(apiMessage(err))),
    [],
  );

  useEffect(() => {
    const signal = { active: true };
    refresh(signal).finally(() => signal.active && setLoading(false));
    return () => {
      signal.active = false;
    };
  }, [refresh]);

  const vnd = (amount: number) =>
    format.number(amount, { style: "currency", currency: "VND", maximumFractionDigits: 0 });

  const topup = async (pkg: TopupPackage) => {
    setPayingId(pkg.id);
    setError(null);
    try {
      const res = await SepayService.createPayment({ requestBody: { amount: pkg.amount } });
      console.log('Payment created:', res);
      setPayment(res);
    } catch (err) {
      setError(apiMessage(err));
    } finally {
      setPayingId(null);
    }
  };

  const onPaymentSuccess = () => {
    void refresh();
  };

  return (
    <div className="settings-wrap">
      {error && <div className="field-error">{error}</div>}

      {payment && (
        <TopupQrModal
          txnRef={payment.txn_ref}
          qrUrl={payment.qr_url}
          amount={payment.amount}
          account={payment.account}
          bank={payment.bank}
          content={payment.content}
          onClose={() => setPayment(null)}
          onSuccess={onPaymentSuccess}
        />
      )}

      <div className="set-panel">
        <div className="sp-head">
          <h3>{t("balanceTitle")}</h3>
          <p>{t("balanceSub")}</p>
        </div>
        <div className="set-row">
          <div className="label">
            <div className="t" style={{ fontFamily: "var(--font-mono)", color: "var(--cyan)", fontSize: 22 }}>
              {loading ? tc("loading") : balance ? vnd(balance.balance) : "—"}
            </div>
            <div className="d">
              {balance ? t("balanceUpdated", { date: formatDate(balance.updated_at) }) : ""}
            </div>
          </div>
          <Wallet size={22} style={{ color: "var(--fg-dim)" }} />
        </div>
      </div>

      <div className="set-panel">
        <div className="sp-head">
          <h3>{t("topupTitle")}</h3>
          <p>{t("topupSub")}</p>
        </div>
        {packages.map((pkg) => (
          <div className="set-row" key={pkg.id}>
            <div className="label">
              <div className="t" style={{ fontFamily: "var(--font-mono)" }}>
                {vnd(pkg.amount)}
              </div>
              <div className="d">{pkg.label}</div>
            </div>
            <button
              className="btn btn-primary"
              onClick={() => void topup(pkg)}
              disabled={payingId !== null}
            >
              {payingId === pkg.id ? (
                <>
                  <RefreshCw size={15} className="spin" /> {tc("loading")}
                </>
              ) : (
                t("payWithSepay")
              )}
            </button>
          </div>
        ))}
        {!loading && packages.length === 0 && (
          <div className="set-row">
            <div className="label">
              <div className="d">{t("noPackages")}</div>
            </div>
          </div>
        )}
      </div>

      <div className="set-panel">
        <div className="sp-head">
          <h3>{t("transactionsTitle")}</h3>
          <p>{t("transactionsSub")}</p>
        </div>
        <table className="tbl">
          <thead>
            <tr>
              <th>{t("colRef")}</th>
              <th>{t("colDate")}</th>
              <th>{t("colType")}</th>
              <th>{t("colAmount")}</th>
              <th>{t("colStatus")}</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr className="empty-row">
                <td colSpan={5}>{tc("loading")}</td>
              </tr>
            )}
            {!loading && transactions.length === 0 && (
              <tr className="empty-row">
                <td colSpan={5}>{t("noTransactions")}</td>
              </tr>
            )}
            {transactions.map((txn) => (
              <tr key={txn.id}>
                <td className="mono-cell">{txn.txn_ref ?? txn.id.slice(0, 8)}</td>
                <td className="mono-cell">{formatDate(txn.created_at)}</td>
                <td className="mono-cell">
                  <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                    {txn.type === "credit" ? (
                      <ArrowUpRight size={13} style={{ color: "var(--ok)" }} />
                    ) : (
                      <ArrowDownRight size={13} style={{ color: "var(--fg-dim)" }} />
                    )}
                    {txn.type === "credit" ? t("typeCredit") : t("typeDebit")}
                  </span>
                </td>
                <td className="mono-cell">{vnd(txn.amount)}</td>
                <td>
                  <span className={`pill ${STATUS_PILL[txn.status]}`}>
                    <span className="dot" />
                    {t(`status_${txn.status}`)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
