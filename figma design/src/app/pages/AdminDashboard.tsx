import { CheckCircle, XCircle, Clock, TrendingUp } from "lucide-react";

const metrics = [
  { label: "Suppliers Export-Ready", value: "87%", icon: CheckCircle, color: "text-green-600" },
  { label: "Suppliers Sample-Ready", value: "92%", icon: CheckCircle, color: "text-blue-600" },
  {
    label: "Sample → Shipment Rate",
    value: "78%",
    icon: TrendingUp,
    color: "text-purple-600",
  },
  { label: "Shipment → Deal Rate", value: "34%", icon: TrendingUp, color: "text-amber-600" },
];

const suppliers = [
  {
    name: "Kerala Estate Co.",
    region: "Malabar",
    exportReady: true,
    sampleReady: true,
    complianceReady: true,
    approvalStatus: "Approved",
  },
  {
    name: "Coorg Valley Farms",
    region: "Coorg",
    exportReady: true,
    sampleReady: true,
    complianceReady: true,
    approvalStatus: "Approved",
  },
  {
    name: "Wayanad Collective",
    region: "Wayanad",
    exportReady: true,
    sampleReady: false,
    complianceReady: true,
    approvalStatus: "Pending Review",
  },
  {
    name: "Chikmagalur Estates",
    region: "Chikmagalur",
    exportReady: true,
    sampleReady: true,
    complianceReady: true,
    approvalStatus: "Approved",
  },
  {
    name: "Nilgiris Coffee Co.",
    region: "Nilgiris",
    exportReady: false,
    sampleReady: true,
    complianceReady: false,
    approvalStatus: "Changes Requested",
  },
];

const inquiries = [
  {
    id: "INQ-001",
    buyer: "Blue Bottle Coffee",
    supplier: "Kerala Estate Co.",
    lot: "Monsooned Malabar AA",
    status: "Shipped",
    courier: "DHL",
    trackingNumber: "1234567890",
    priorNoticeFiled: true,
    priorNoticeFiledBy: "Supplier",
  },
  {
    id: "INQ-002",
    buyer: "Intelligentsia Coffee",
    supplier: "Coorg Valley Farms",
    lot: "Arabica Shade Grown",
    status: "Sample Preparing",
    courier: null,
    trackingNumber: null,
    priorNoticeFiled: false,
    priorNoticeFiledBy: "Freight Forwarder",
  },
  {
    id: "INQ-003",
    buyer: "Counter Culture",
    supplier: "Chikmagalur Estates",
    lot: "Estate Reserve Arabica",
    status: "Approved",
    courier: null,
    trackingNumber: null,
    priorNoticeFiled: false,
    priorNoticeFiledBy: "Buyer",
  },
  {
    id: "INQ-004",
    buyer: "Stumptown Coffee",
    supplier: "Kerala Estate Co.",
    lot: "Monsooned Malabar AA",
    status: "Prior Notice Pending",
    courier: "FedEx",
    trackingNumber: "9876543210",
    priorNoticeFiled: false,
    priorNoticeFiledBy: "Supplier",
  },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "Approved":
      return "bg-green-100 text-green-800";
    case "Pending Review":
      return "bg-yellow-100 text-yellow-800";
    case "Changes Requested":
      return "bg-red-100 text-red-800";
    case "Shipped":
      return "bg-blue-100 text-blue-800";
    case "Sample Preparing":
      return "bg-purple-100 text-purple-800";
    case "Prior Notice Pending":
      return "bg-orange-100 text-orange-800";
    default:
      return "bg-gray-100 text-gray-800";
  }
};

export function AdminDashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold mb-2">Admin Dashboard</h1>
          <p className="text-gray-600">Manage supplier readiness and inquiry operations</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <div className="grid md:grid-cols-4 gap-6">
          {metrics.map((metric, index) => {
            const Icon = metric.icon;
            return (
              <div key={index} className="bg-white rounded-lg border p-6">
                <div className="flex items-center justify-between mb-2">
                  <Icon className={`w-8 h-8 ${metric.color}`} />
                </div>
                <p className="text-3xl font-bold mb-1">{metric.value}</p>
                <p className="text-sm text-gray-600">{metric.label}</p>
              </div>
            );
          })}
        </div>

        <div className="bg-white rounded-lg border">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Supplier Readiness</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Supplier
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Region
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Export Ready
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sample Ready
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Compliance Ready
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {suppliers.map((supplier, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">{supplier.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {supplier.region}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      {supplier.exportReady ? (
                        <CheckCircle className="w-5 h-5 text-green-600 mx-auto" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-600 mx-auto" />
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      {supplier.sampleReady ? (
                        <CheckCircle className="w-5 h-5 text-green-600 mx-auto" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-600 mx-auto" />
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      {supplier.complianceReady ? (
                        <CheckCircle className="w-5 h-5 text-green-600 mx-auto" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-600 mx-auto" />
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${getStatusColor(
                          supplier.approvalStatus
                        )}`}
                      >
                        {supplier.approvalStatus}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex gap-2">
                        <button className="text-amber-700 hover:text-amber-900">View</button>
                        {supplier.approvalStatus === "Pending Review" && (
                          <>
                            <span className="text-gray-300">|</span>
                            <button className="text-green-600 hover:text-green-800">
                              Approve
                            </button>
                          </>
                        )}
                        {supplier.approvalStatus === "Approved" && (
                          <>
                            <span className="text-gray-300">|</span>
                            <button className="text-blue-600 hover:text-blue-800">Edit</button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-lg border">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Inquiry Pipeline</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Buyer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Supplier
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Lot
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Courier
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tracking
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Prior Notice
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Filed By
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {inquiries.map((inquiry) => (
                  <tr key={inquiry.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {inquiry.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {inquiry.buyer}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {inquiry.supplier}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">
                      {inquiry.lot}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${getStatusColor(
                          inquiry.status
                        )}`}
                      >
                        {inquiry.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {inquiry.courier || "-"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-xs text-gray-600">
                      {inquiry.trackingNumber || "-"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      {inquiry.priorNoticeFiled ? (
                        <CheckCircle className="w-5 h-5 text-green-600 mx-auto" />
                      ) : (
                        <Clock className="w-5 h-5 text-yellow-600 mx-auto" />
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {inquiry.priorNoticeFiledBy}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
