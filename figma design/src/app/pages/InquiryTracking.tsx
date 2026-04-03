import { CheckCircle, Circle, Clock } from "lucide-react";

const mockInquiries = [
  {
    id: "INQ-001",
    coffeeLot: "Monsooned Malabar AA",
    supplier: "Kerala Estate Co.",
    buyer: "Blue Bottle Coffee",
    requestedDate: "2026-03-10",
    status: "Shipped",
    timeline: [
      { stage: "New", date: "2026-03-10", completed: true },
      { stage: "Approved", date: "2026-03-10", completed: true },
      { stage: "Sample Preparing", date: "2026-03-11", completed: true },
      { stage: "Prior Notice Pending", date: "2026-03-12", completed: true },
      { stage: "Shipped", date: "2026-03-13", completed: true },
      { stage: "Delivered", date: null, completed: false },
      { stage: "Closed", date: null, completed: false },
    ],
    shipment: {
      courier: "DHL",
      trackingNumber: "1234567890",
      shipDate: "2026-03-13",
      estimatedArrival: "2026-03-18",
    },
    compliance: {
      priorNoticeRequired: true,
      priorNoticeFiled: true,
      filedBy: "Supplier",
    },
  },
  {
    id: "INQ-002",
    coffeeLot: "Arabica Shade Grown",
    supplier: "Coorg Valley Farms",
    buyer: "Intelligentsia Coffee",
    requestedDate: "2026-03-15",
    status: "Approved",
    timeline: [
      { stage: "New", date: "2026-03-15", completed: true },
      { stage: "Approved", date: "2026-03-16", completed: true },
      { stage: "Sample Preparing", date: null, completed: false },
      { stage: "Prior Notice Pending", date: null, completed: false },
      { stage: "Shipped", date: null, completed: false },
      { stage: "Delivered", date: null, completed: false },
      { stage: "Closed", date: null, completed: false },
    ],
    shipment: null,
    compliance: {
      priorNoticeRequired: true,
      priorNoticeFiled: false,
      filedBy: "Freight Forwarder",
    },
  },
];

export function InquiryTracking() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold mb-2">Sample Inquiries</h1>
          <p className="text-gray-600">Track your sample requests and shipments</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {mockInquiries.map((inquiry) => (
          <div key={inquiry.id} className="bg-white rounded-lg border overflow-hidden">
            <div className="p-6 border-b bg-gray-50">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold mb-1">{inquiry.coffeeLot}</h2>
                  <p className="text-sm text-gray-600">
                    {inquiry.supplier} • Request #{inquiry.id}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    inquiry.status === "Shipped"
                      ? "bg-blue-100 text-blue-800"
                      : "bg-green-100 text-green-800"
                  }`}
                >
                  {inquiry.status}
                </span>
              </div>
              <p className="text-sm text-gray-600">
                Requested by {inquiry.buyer} on{" "}
                {new Date(inquiry.requestedDate).toLocaleDateString()}
              </p>
            </div>

            <div className="p-6">
              <h3 className="font-semibold mb-6">Sample Timeline</h3>
              <div className="space-y-6">
                {inquiry.timeline.map((step, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      {step.completed ? (
                        <CheckCircle className="w-6 h-6 text-green-600" />
                      ) : index === inquiry.timeline.findIndex((s) => !s.completed) ? (
                        <Clock className="w-6 h-6 text-blue-600" />
                      ) : (
                        <Circle className="w-6 h-6 text-gray-300" />
                      )}
                      {index < inquiry.timeline.length - 1 && (
                        <div
                          className={`w-0.5 h-12 mt-2 ${
                            step.completed ? "bg-green-600" : "bg-gray-200"
                          }`}
                        />
                      )}
                    </div>
                    <div className="flex-1 pb-8">
                      <p
                        className={`font-medium ${
                          step.completed
                            ? "text-gray-900"
                            : index === inquiry.timeline.findIndex((s) => !s.completed)
                            ? "text-blue-900"
                            : "text-gray-400"
                        }`}
                      >
                        {step.stage}
                      </p>
                      {step.date && (
                        <p className="text-sm text-gray-600">
                          {new Date(step.date).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6 p-6 border-t bg-gray-50">
              <div>
                <h3 className="font-semibold mb-4">Shipment Details</h3>
                {inquiry.shipment ? (
                  <dl className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <dt className="text-gray-600">Courier</dt>
                      <dd className="font-medium">{inquiry.shipment.courier}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-600">Tracking Number</dt>
                      <dd className="font-medium font-mono text-xs">
                        {inquiry.shipment.trackingNumber}
                      </dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-600">Ship Date</dt>
                      <dd className="font-medium">
                        {new Date(inquiry.shipment.shipDate).toLocaleDateString()}
                      </dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-600">Est. Arrival</dt>
                      <dd className="font-medium">
                        {new Date(inquiry.shipment.estimatedArrival).toLocaleDateString()}
                      </dd>
                    </div>
                  </dl>
                ) : (
                  <p className="text-sm text-gray-600">Not yet shipped</p>
                )}
              </div>

              <div>
                <h3 className="font-semibold mb-4">Compliance</h3>
                <dl className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-gray-600">Prior Notice Required</dt>
                    <dd className="font-medium">
                      {inquiry.compliance.priorNoticeRequired ? "Yes" : "No"}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-600">Prior Notice Filed</dt>
                    <dd>
                      {inquiry.compliance.priorNoticeFiled ? (
                        <span className="flex items-center gap-1 text-green-700">
                          <CheckCircle className="w-4 h-4" />
                          <span className="font-medium">Yes</span>
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-yellow-700">
                          <Clock className="w-4 h-4" />
                          <span className="font-medium">Pending</span>
                        </span>
                      )}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-600">Filed By</dt>
                    <dd className="font-medium">{inquiry.compliance.filedBy}</dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
