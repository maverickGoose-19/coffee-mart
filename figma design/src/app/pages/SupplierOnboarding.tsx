import { useState } from "react";
import { CheckCircle, Circle, AlertCircle } from "lucide-react";

type Step = "basic" | "estate" | "export" | "sample" | "compliance" | "review";

const steps: { id: Step; label: string }[] = [
  { id: "basic", label: "Basic Info" },
  { id: "estate", label: "Estate Info" },
  { id: "export", label: "Export Readiness" },
  { id: "sample", label: "Sample Shipping" },
  { id: "compliance", label: "Compliance Responsibility" },
  { id: "review", label: "Review" },
];

export function SupplierOnboarding() {
  const [currentStep, setCurrentStep] = useState<Step>("basic");
  const [formData, setFormData] = useState({
    companyName: "",
    contactName: "",
    contactEmail: "",
    contactPhone: "",
    region: "",
    website: "",
    altitude: "",
    varietals: "",
    certifications: [] as string[],
    estateDescription: "",
    exportsInternationally: false,
    exportPartner: "",
    exportTerms: "",
    minExportOrder: "",
    hasCertificateOfOrigin: false,
    hasPhytosanitaryCert: false,
    hasInvoiceCapability: false,
    canShipSamples: false,
    sampleSize: "",
    couriers: [] as string[],
    sampleShippingPaidBy: "",
    samplePrepDays: "",
    sampleShippingDays: "",
    samplePrice: "",
    priorNoticeHandler: "",
  });

  const currentStepIndex = steps.findIndex((s) => s.id === currentStep);

  const getStepStatus = (stepId: Step) => {
    const stepIndex = steps.findIndex((s) => s.id === stepId);
    if (stepIndex < currentStepIndex) return "completed";
    if (stepIndex === currentStepIndex) return "current";
    return "upcoming";
  };

  const updateFormData = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const toggleArrayValue = (field: string, value: string) => {
    setFormData((prev) => {
      const currentArray = prev[field as keyof typeof prev] as string[];
      const newArray = currentArray.includes(value)
        ? currentArray.filter((v) => v !== value)
        : [...currentArray, value];
      return { ...prev, [field]: newArray };
    });
  };

  const exportReady =
    formData.exportsInternationally &&
    formData.exportPartner &&
    formData.hasCertificateOfOrigin &&
    formData.hasPhytosanitaryCert;

  const sampleReady =
    formData.canShipSamples && formData.sampleSize && formData.couriers.length > 0;

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r p-6 sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto">
        <h2 className="font-semibold mb-6">Supplier Onboarding</h2>
        <nav className="space-y-2">
          {steps.map((step) => {
            const status = getStepStatus(step.id);
            return (
              <button
                key={step.id}
                onClick={() => setCurrentStep(step.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  status === "current"
                    ? "bg-amber-50 text-amber-900"
                    : status === "completed"
                    ? "text-green-700 hover:bg-gray-50"
                    : "text-gray-600 hover:bg-gray-50"
                }`}
              >
                {status === "completed" ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <Circle className="w-5 h-5" />
                )}
                <span className="text-sm">{step.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="flex-1 p-8">
        <div className="max-w-3xl">
          {currentStep === "basic" && (
            <div>
              <h1 className="text-2xl font-bold mb-6">Basic Information</h1>
              <div className="bg-white rounded-lg border p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Company Name *</label>
                  <input
                    type="text"
                    value={formData.companyName}
                    onChange={(e) => updateFormData("companyName", e.target.value)}
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Contact Name *</label>
                  <input
                    type="text"
                    value={formData.contactName}
                    onChange={(e) => updateFormData("contactName", e.target.value)}
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Contact Email *</label>
                  <input
                    type="email"
                    value={formData.contactEmail}
                    onChange={(e) => updateFormData("contactEmail", e.target.value)}
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Contact Phone *</label>
                  <input
                    type="tel"
                    value={formData.contactPhone}
                    onChange={(e) => updateFormData("contactPhone", e.target.value)}
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Region *</label>
                  <select
                    value={formData.region}
                    onChange={(e) => updateFormData("region", e.target.value)}
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    <option value="">Select region</option>
                    <option value="coorg">Coorg</option>
                    <option value="wayanad">Wayanad</option>
                    <option value="malabar">Malabar</option>
                    <option value="nilgiris">Nilgiris</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Website</label>
                  <input
                    type="url"
                    value={formData.website}
                    onChange={(e) => updateFormData("website", e.target.value)}
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>
              </div>
            </div>
          )}

          {currentStep === "estate" && (
            <div>
              <h1 className="text-2xl font-bold mb-6">Estate Information</h1>
              <div className="bg-white rounded-lg border p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Altitude (meters)</label>
                  <input
                    type="text"
                    value={formData.altitude}
                    onChange={(e) => updateFormData("altitude", e.target.value)}
                    className="w-full px-3 py-2 border rounded-md"
                    placeholder="e.g., 1200-1500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Varietals</label>
                  <input
                    type="text"
                    value={formData.varietals}
                    onChange={(e) => updateFormData("varietals", e.target.value)}
                    className="w-full px-3 py-2 border rounded-md"
                    placeholder="e.g., Arabica, Robusta, S795"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Certifications</label>
                  <div className="space-y-2">
                    {["Organic", "Fair Trade", "Rainforest Alliance", "UTZ"].map((cert) => (
                      <label key={cert} className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={formData.certifications.includes(cert)}
                          onChange={() => toggleArrayValue("certifications", cert)}
                          className="rounded"
                        />
                        <span className="text-sm">{cert}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Estate Description</label>
                  <textarea
                    value={formData.estateDescription}
                    onChange={(e) => updateFormData("estateDescription", e.target.value)}
                    className="w-full px-3 py-2 border rounded-md h-32"
                    placeholder="Tell buyers about your estate's story, practices, and heritage"
                  />
                </div>
              </div>
            </div>
          )}

          {currentStep === "export" && (
            <div>
              <h1 className="text-2xl font-bold mb-6">Export Readiness</h1>
              <div className="bg-white rounded-lg border p-6 space-y-6">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <span className="font-medium">Export Ready Status:</span>
                  {exportReady ? (
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                      Export Ready
                    </span>
                  ) : (
                    <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                      Missing Info
                    </span>
                  )}
                </div>

                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.exportsInternationally}
                      onChange={(e) =>
                        updateFormData("exportsInternationally", e.target.checked)
                      }
                      className="rounded"
                    />
                    <span className="font-medium">Exports internationally</span>
                  </label>
                </div>

                {formData.exportsInternationally && (
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Export Partner Name *
                      </label>
                      <input
                        type="text"
                        value={formData.exportPartner}
                        onChange={(e) => updateFormData("exportPartner", e.target.value)}
                        className="w-full px-3 py-2 border rounded-md"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Export Terms</label>
                      <select
                        value={formData.exportTerms}
                        onChange={(e) => updateFormData("exportTerms", e.target.value)}
                        className="w-full px-3 py-2 border rounded-md"
                      >
                        <option value="">Select terms</option>
                        <option value="FOB">FOB (Free on Board)</option>
                        <option value="EXW">EXW (Ex Works)</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Minimum Export Order (kg)
                      </label>
                      <input
                        type="number"
                        value={formData.minExportOrder}
                        onChange={(e) => updateFormData("minExportOrder", e.target.value)}
                        className="w-full px-3 py-2 border rounded-md"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Documentation Available *
                      </label>
                      <div className="space-y-2">
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={formData.hasCertificateOfOrigin}
                            onChange={(e) =>
                              updateFormData("hasCertificateOfOrigin", e.target.checked)
                            }
                            className="rounded"
                          />
                          <span className="text-sm">Certificate of Origin</span>
                        </label>
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={formData.hasPhytosanitaryCert}
                            onChange={(e) =>
                              updateFormData("hasPhytosanitaryCert", e.target.checked)
                            }
                            className="rounded"
                          />
                          <span className="text-sm">Phytosanitary Certificate</span>
                        </label>
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={formData.hasInvoiceCapability}
                            onChange={(e) =>
                              updateFormData("hasInvoiceCapability", e.target.checked)
                            }
                            className="rounded"
                          />
                          <span className="text-sm">Invoice Capability</span>
                        </label>
                      </div>
                    </div>
                  </>
                )}

                {!exportReady && formData.exportsInternationally && (
                  <div className="flex gap-2 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-yellow-800">
                      Please complete all required fields to achieve Export Ready status
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {currentStep === "sample" && (
            <div>
              <h1 className="text-2xl font-bold mb-6">Sample Shipping Capability</h1>
              <div className="bg-white rounded-lg border p-6 space-y-6">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <span className="font-medium">Sample Ready Status:</span>
                  {sampleReady ? (
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                      Sample Ready
                    </span>
                  ) : (
                    <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                      Missing Info
                    </span>
                  )}
                </div>

                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.canShipSamples}
                      onChange={(e) => updateFormData("canShipSamples", e.target.checked)}
                      className="rounded"
                    />
                    <span className="font-medium">Can ship samples</span>
                  </label>
                </div>

                {formData.canShipSamples && (
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Sample Size (grams) *
                      </label>
                      <input
                        type="number"
                        value={formData.sampleSize}
                        onChange={(e) => updateFormData("sampleSize", e.target.value)}
                        className="w-full px-3 py-2 border rounded-md"
                        placeholder="e.g., 200"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Courier Options *
                      </label>
                      <div className="space-y-2">
                        {["DHL", "FedEx", "UPS"].map((courier) => (
                          <label key={courier} className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={formData.couriers.includes(courier)}
                              onChange={() => toggleArrayValue("couriers", courier)}
                              className="rounded"
                            />
                            <span className="text-sm">{courier}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Sample Shipping Paid By
                      </label>
                      <select
                        value={formData.sampleShippingPaidBy}
                        onChange={(e) => updateFormData("sampleShippingPaidBy", e.target.value)}
                        className="w-full px-3 py-2 border rounded-md"
                      >
                        <option value="">Select option</option>
                        <option value="supplier">Supplier</option>
                        <option value="buyer">Buyer</option>
                        <option value="shared">Shared</option>
                      </select>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Sample Prep Days
                        </label>
                        <input
                          type="number"
                          value={formData.samplePrepDays}
                          onChange={(e) => updateFormData("samplePrepDays", e.target.value)}
                          className="w-full px-3 py-2 border rounded-md"
                          placeholder="e.g., 2"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Sample Shipping Days
                        </label>
                        <input
                          type="number"
                          value={formData.sampleShippingDays}
                          onChange={(e) => updateFormData("sampleShippingDays", e.target.value)}
                          className="w-full px-3 py-2 border rounded-md"
                          placeholder="e.g., 5"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Sample Price (USD)</label>
                      <input
                        type="number"
                        value={formData.samplePrice}
                        onChange={(e) => updateFormData("samplePrice", e.target.value)}
                        className="w-full px-3 py-2 border rounded-md"
                        placeholder="e.g., 15"
                      />
                    </div>
                  </>
                )}
              </div>
            </div>
          )}

          {currentStep === "compliance" && (
            <div>
              <h1 className="text-2xl font-bold mb-6">Compliance Responsibility</h1>
              <div className="bg-white rounded-lg border p-6 space-y-6">
                <div className="flex gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-blue-900 mb-1">
                      FDA Prior Notice Required
                    </p>
                    <p className="text-sm text-blue-800">
                      US-bound food sample shipments require FDA Prior Notice filing before
                      arrival. Please specify who will handle this responsibility.
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-3">
                    Who handles FDA Prior Notice for US sample shipments? *
                  </label>
                  <div className="space-y-3">
                    {[
                      { value: "supplier", label: "Supplier" },
                      { value: "buyer", label: "Buyer" },
                      { value: "broker", label: "Freight Forwarder / Broker" },
                    ].map((option) => (
                      <label
                        key={option.value}
                        className="flex items-center gap-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50"
                      >
                        <input
                          type="radio"
                          name="priorNoticeHandler"
                          value={option.value}
                          checked={formData.priorNoticeHandler === option.value}
                          onChange={(e) => updateFormData("priorNoticeHandler", e.target.value)}
                          className="text-amber-700"
                        />
                        <span>{option.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {currentStep === "review" && (
            <div>
              <h1 className="text-2xl font-bold mb-6">Review & Submit</h1>
              <div className="space-y-6">
                <div className="bg-white rounded-lg border p-6">
                  <h3 className="font-semibold mb-4">Basic Information</h3>
                  <dl className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <dt className="text-gray-600">Company</dt>
                      <dd className="font-medium">{formData.companyName || "-"}</dd>
                    </div>
                    <div>
                      <dt className="text-gray-600">Contact</dt>
                      <dd className="font-medium">{formData.contactName || "-"}</dd>
                    </div>
                    <div>
                      <dt className="text-gray-600">Email</dt>
                      <dd className="font-medium">{formData.contactEmail || "-"}</dd>
                    </div>
                    <div>
                      <dt className="text-gray-600">Region</dt>
                      <dd className="font-medium capitalize">{formData.region || "-"}</dd>
                    </div>
                  </dl>
                </div>

                <div className="bg-white rounded-lg border p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold">Export Readiness</h3>
                    {exportReady ? (
                      <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                        Export Ready
                      </span>
                    ) : (
                      <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
                        Missing Info
                      </span>
                    )}
                  </div>
                  <dl className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <dt className="text-gray-600">Export Partner</dt>
                      <dd className="font-medium">{formData.exportPartner || "-"}</dd>
                    </div>
                    <div>
                      <dt className="text-gray-600">Export Terms</dt>
                      <dd className="font-medium">{formData.exportTerms || "-"}</dd>
                    </div>
                  </dl>
                </div>

                <div className="bg-white rounded-lg border p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold">Sample Shipping</h3>
                    {sampleReady ? (
                      <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                        Sample Ready
                      </span>
                    ) : (
                      <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
                        Missing Info
                      </span>
                    )}
                  </div>
                  <dl className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <dt className="text-gray-600">Sample Size</dt>
                      <dd className="font-medium">{formData.sampleSize ? `${formData.sampleSize}g` : "-"}</dd>
                    </div>
                    <div>
                      <dt className="text-gray-600">Couriers</dt>
                      <dd className="font-medium">{formData.couriers.join(", ") || "-"}</dd>
                    </div>
                  </dl>
                </div>

                <div className="bg-white rounded-lg border p-6">
                  <h3 className="font-semibold mb-4">Compliance</h3>
                  <dl className="text-sm">
                    <dt className="text-gray-600">FDA Prior Notice Handler</dt>
                    <dd className="font-medium capitalize">{formData.priorNoticeHandler || "-"}</dd>
                  </dl>
                </div>

                {(!exportReady || !sampleReady || !formData.priorNoticeHandler) && (
                  <div className="flex gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-800">
                      Please complete all required sections before submitting for approval
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="flex justify-between mt-8 pt-6 border-t">
            <button
              onClick={() => {
                const prevIndex = Math.max(0, currentStepIndex - 1);
                setCurrentStep(steps[prevIndex].id);
              }}
              disabled={currentStepIndex === 0}
              className="px-6 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <div className="flex gap-3">
              <button className="px-6 py-2 border rounded-lg hover:bg-gray-50">
                Save Draft
              </button>
              {currentStepIndex < steps.length - 1 ? (
                <button
                  onClick={() => {
                    const nextIndex = Math.min(steps.length - 1, currentStepIndex + 1);
                    setCurrentStep(steps[nextIndex].id);
                  }}
                  className="px-6 py-2 bg-amber-700 text-white rounded-lg hover:bg-amber-800"
                >
                  Next
                </button>
              ) : (
                <button className="px-6 py-2 bg-amber-700 text-white rounded-lg hover:bg-amber-800">
                  Submit for Approval
                </button>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
