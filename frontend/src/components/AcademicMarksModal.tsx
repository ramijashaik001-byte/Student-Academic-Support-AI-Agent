import React, { useState } from "react";
import { X, Upload, CheckCircle, AlertTriangle, FileText, Download } from "lucide-react";
import { apiClient } from "../api/client";

interface AcademicMarksModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImportSuccess?: () => void;
}

export const AcademicMarksModal: React.FC<AcademicMarksModalProps> = ({
  isOpen,
  onClose,
  onImportSuccess,
}) => {
  const [selectedSemester, setSelectedSemester] = useState("1-1");
  const [academicYear, setAcademicYear] = useState("2023-2024");
  const [sessionTitle, setSessionTitle] = useState("Regular Semester Examination");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setPreviewData(null);
      setErrorMessage("");
      setSuccessMessage("");
    }
  };

  const handleValidate = async () => {
    if (!file) {
      setErrorMessage("Please select a marksheet CSV file first.");
      return;
    }

    setLoading(true);
    setErrorMessage("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("semester_label", selectedSemester);
      formData.append("academic_year", academicYear);
      formData.append("session_title", sessionTitle);

      const res = await apiClient.validateMarksCsv(formData);
      setPreviewData(res.data);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || "Error parsing marksheet CSV.");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!previewData) return;
    setLoading(true);
    setErrorMessage("");
    try {
      const res = await apiClient.confirmMarksImport(previewData);
      setSuccessMessage(res.data.message || "Marks imported successfully!");
      if (onImportSuccess) onImportSuccess();
      setTimeout(() => {
        onClose();
        setSuccessMessage("");
        setPreviewData(null);
        setFile(null);
      }, 1500);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || "Failed to commit marksheet.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl border border-[#E8E6E1] shadow-xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-5 py-4 border-b border-[#E8E6E1] flex items-center justify-between bg-[#FAF9F6]">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-[#EBE5FC] border border-[#DDD6FE] text-[#5B4F8A] flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-[#2D3139]">Import Official Marksheet (CSV)</h3>
              <p className="text-[11px] text-[#6C727F]">
                Validate and record verified semester results under R23 regulations
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-[#9CA3AF] hover:text-[#2D3139] p-1 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 overflow-y-auto space-y-4 text-xs">
          {/* Controls row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-[#4B515D] mb-1">
                Semester
              </label>
              <select
                value={selectedSemester}
                onChange={(e) => {
                  setSelectedSemester(e.target.value);
                  setPreviewData(null);
                }}
                className="w-full bg-[#FAF9F6] border border-[#E2DFD7] rounded-lg px-2.5 py-1.5 text-xs text-[#2D3139] focus:outline-none focus:ring-1 focus:ring-[#7C6EB0]"
              >
                {["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"].map((sem) => (
                  <option key={sem} value={sem}>
                    Semester {sem}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-[#4B515D] mb-1">
                Academic Year
              </label>
              <input
                type="text"
                value={academicYear}
                onChange={(e) => setAcademicYear(e.target.value)}
                className="w-full bg-[#FAF9F6] border border-[#E2DFD7] rounded-lg px-2.5 py-1.5 text-xs text-[#2D3139] focus:outline-none focus:ring-1 focus:ring-[#7C6EB0]"
                placeholder="2023-2024"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-[#4B515D] mb-1">
                Session Title
              </label>
              <input
                type="text"
                value={sessionTitle}
                onChange={(e) => setSessionTitle(e.target.value)}
                className="w-full bg-[#FAF9F6] border border-[#E2DFD7] rounded-lg px-2.5 py-1.5 text-xs text-[#2D3139] focus:outline-none focus:ring-1 focus:ring-[#7C6EB0]"
                placeholder="Regular Dec 2023"
              />
            </div>
          </div>

          {/* File Picker & Template Link */}
          <div className="border-2 border-dashed border-[#DDD6FE] rounded-xl p-4 bg-[#FAF9F6]/60 flex flex-col items-center justify-center text-center space-y-2">
            <Upload className="w-6 h-6 text-[#7C6EB0]" />
            <div>
              <label className="cursor-pointer text-xs font-semibold text-[#5B4F8A] hover:underline">
                <span>Select Marksheet CSV file</span>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
              {file ? (
                <div className="text-[11px] text-[#2D3139] font-medium mt-1">
                  Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
                </div>
              ) : (
                <div className="text-[11px] text-[#6C727F] mt-1">
                  Only .csv files supported
                </div>
              )}
            </div>
            <a
              href="/api/academic/templates/marks"
              download
              className="text-[11px] text-[#62826F] hover:underline flex items-center gap-1 font-medium pt-1"
            >
              <Download className="w-3 h-3" />
              <span>Download Official Marks CSV Template</span>
            </a>
          </div>

          {/* Validation Error / Success */}
          {errorMessage && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {successMessage && (
            <div className="p-3 bg-green-50 border border-green-200 text-green-700 rounded-xl flex items-center gap-2">
              <CheckCircle className="w-4 h-4 shrink-0" />
              <span>{successMessage}</span>
            </div>
          )}

          {/* Validation Preview Table */}
          {previewData && (
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between p-3 bg-[#EBE5FC]/40 border border-[#DDD6FE] rounded-xl">
                <div>
                  <span className="font-semibold text-[#5B4F8A]">
                    Parsed: {previewData.total_parsed_subjects} Subjects
                  </span>
                  <span className="text-[#6C727F] ml-2">
                    ({previewData.total_credits} Credits)
                  </span>
                </div>
                <div className="font-bold text-[#2D3139]">
                  Computed SGPA: <span className="text-[#5B4F8A]">{previewData.computed_sgpa}</span>
                </div>
              </div>

              {previewData.warnings && previewData.warnings.length > 0 && (
                <div className="p-3 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl text-[11px] space-y-1">
                  <div className="font-semibold flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Validation Notices:</span>
                  </div>
                  {previewData.warnings.map((w: string, i: number) => (
                    <div key={i}>• {w}</div>
                  ))}
                </div>
              )}

              <div className="max-h-48 overflow-y-auto border border-[#E8E6E1] rounded-xl overflow-hidden">
                <table className="w-full text-left border-collapse text-[11px]">
                  <thead>
                    <tr className="bg-[#FAF9F6] border-b border-[#E8E6E1] text-[#6C727F]">
                      <th className="p-2 font-semibold">Code</th>
                      <th className="p-2 font-semibold">Subject</th>
                      <th className="p-2 font-semibold text-center">Cr</th>
                      <th className="p-2 font-semibold text-center">Int</th>
                      <th className="p-2 font-semibold text-center">Ext</th>
                      <th className="p-2 font-semibold text-center">Tot</th>
                      <th className="p-2 font-semibold text-center">Grade</th>
                      <th className="p-2 font-semibold text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {previewData.subjects.map((s: any, idx: number) => (
                      <tr key={idx} className="border-b border-[#F0EFEB] hover:bg-[#FAF9F6]/50">
                        <td className="p-2 font-mono text-[10px]">{s.subject_code}</td>
                        <td className="p-2 font-medium">{s.subject_name}</td>
                        <td className="p-2 text-center">{s.credits}</td>
                        <td className="p-2 text-center">{s.internal_marks}</td>
                        <td className="p-2 text-center">{s.external_marks}</td>
                        <td className="p-2 text-center font-semibold">{s.total_marks}</td>
                        <td className="p-2 text-center font-bold text-[#5B4F8A]">{s.grade}</td>
                        <td className="p-2 text-center">
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                              s.pass_fail_status === "PASS"
                                ? "bg-green-100 text-green-700"
                                : "bg-red-100 text-red-700"
                            }`}
                          >
                            {s.pass_fail_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-[#E8E6E1] bg-[#FAF9F6] flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 bg-white border border-[#E2DFD7] text-[#4B515D] rounded-xl hover:bg-gray-50 transition-colors font-medium"
          >
            Cancel
          </button>
          {!previewData ? (
            <button
              onClick={handleValidate}
              disabled={loading || !file}
              className="px-4 py-1.5 bg-[#5B4F8A] hover:bg-[#4E4377] text-white rounded-xl font-medium shadow-xs transition-colors disabled:opacity-50 flex items-center gap-1.5"
            >
              <Upload className="w-3.5 h-3.5" />
              <span>{loading ? "Validating..." : "Validate CSV"}</span>
            </button>
          ) : (
            <button
              onClick={handleConfirm}
              disabled={loading || !previewData.can_confirm}
              className="px-4 py-1.5 bg-[#62826F] hover:bg-[#526D5D] text-white rounded-xl font-medium shadow-xs transition-colors disabled:opacity-50 flex items-center gap-1.5"
            >
              <CheckCircle className="w-3.5 h-3.5" />
              <span>{loading ? "Saving..." : "Confirm & Save Results"}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
