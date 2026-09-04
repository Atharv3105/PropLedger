import React, { useEffect, useState } from 'react';
import { propertiesApi, unitsApi } from '../services/api';
import { Property, Unit, PropertyOccupancy } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Modal } from '../components/common/Modal';
import { Building2, Search, MapPin, Layers, Home } from 'lucide-react';

export const PropertiesPage: React.FC = () => {
  const [properties, setProperties] = useState<Property[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  
  // Units Drawer
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [occupancyStats, setOccupancyStats] = useState<PropertyOccupancy | null>(null);
  const [units, setUnits] = useState<Unit[]>([]);
  const [loadingUnits, setLoadingUnits] = useState(false);

  const fetchProperties = () => {
    setLoading(true);
    propertiesApi
      .list(100, 0, search)
      .then(setProperties)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchProperties();
  }, [search]);

  const handleInspectUnits = async (prop: Property) => {
    setSelectedProperty(prop);
    setLoadingUnits(true);
    try {
      const [unitsData, occData] = await Promise.all([
        unitsApi.list(100, 0, prop.property_id),
        propertiesApi.getOccupancy(prop.property_id).catch(() => null),
      ]);
      setUnits(unitsData);
      setOccupancyStats(occData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingUnits(false);
    }
  };

  return (
    <div className="space-y-5">
      {/* Top Header Controls */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Properties & Asset Catalog</h2>
          <p className="text-xs text-slate-500">Real estate parcels, building compositions, and unit capacities</p>
        </div>
        <div className="relative w-72">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search property or city..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-white border border-slate-200 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Querying properties and unit counts..." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {properties.map((prop) => (
            <Card key={prop.property_id} className="hover:border-slate-300 transition flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
                    {prop.property_code}
                  </span>
                  <Badge variant={prop.property_type === 'COMMERCIAL' ? 'purple' : 'info'}>
                    {prop.property_type || 'RESIDENTIAL'}
                  </Badge>
                </div>
                <h3 className="text-base font-bold text-slate-900 mt-2">{prop.property_name}</h3>
                <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  <span>{prop.city}, {prop.state}</span>
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between text-xs">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1 text-slate-600">
                    <Layers className="w-3.5 h-3.5 text-slate-400" />
                    <span><strong>{prop.total_buildings}</strong> Bldgs</span>
                  </div>
                  <div className="flex items-center gap-1 text-slate-600">
                    <Home className="w-3.5 h-3.5 text-slate-400" />
                    <span><strong>{prop.total_units}</strong> Units</span>
                  </div>
                </div>

                <button
                  onClick={() => handleInspectUnits(prop)}
                  className="px-2.5 py-1 bg-slate-100 hover:bg-emerald-50 text-slate-700 hover:text-emerald-700 rounded font-semibold text-xs transition"
                >
                  Units ({prop.total_units}) →
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Property Units Modal */}
      <Modal
        isOpen={!!selectedProperty}
        onClose={() => setSelectedProperty(null)}
        title={selectedProperty?.property_name || 'Property Units'}
        subtitle={`${selectedProperty?.property_code} • ${selectedProperty?.city}, ${selectedProperty?.state}`}
        maxWidth="max-w-3xl"
      >
        {loadingUnits ? (
          <LoadingSpinner message="Fetching units from database..." />
        ) : (
          <div className="space-y-4">
            {occupancyStats && (
              <div className="grid grid-cols-4 gap-2 bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs">
                <div>
                  <span className="text-slate-500">Total Units:</span>
                  <p className="font-bold text-slate-900">{occupancyStats.total_units}</p>
                </div>
                <div>
                  <span className="text-emerald-600 font-semibold">Occupied:</span>
                  <p className="font-bold text-slate-900">{occupancyStats.occupied_units}</p>
                </div>
                <div>
                  <span className="text-slate-500">Vacant:</span>
                  <p className="font-bold text-slate-900">{occupancyStats.vacant_units}</p>
                </div>
                <div>
                  <span className="text-slate-500">Occupancy %:</span>
                  <p className="font-bold text-emerald-700">{Number(occupancyStats.occupancy_rate_pct).toFixed(1)}%</p>
                </div>
              </div>
            )}

            <div className="overflow-x-auto border border-slate-200 rounded-lg max-h-96">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100/70 text-slate-600 font-bold border-b border-slate-200 sticky top-0">
                  <tr>
                    <th className="p-2.5">Unit #</th>
                    <th className="p-2.5">Building</th>
                    <th className="p-2.5">Type</th>
                    <th className="p-2.5">Status</th>
                    <th className="p-2.5 text-right">Market Rent</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {units.map((u) => (
                    <tr key={u.unit_id} className="hover:bg-slate-50">
                      <td className="p-2.5 font-bold text-slate-900">{u.unit_number}</td>
                      <td className="p-2.5 text-slate-600">{u.building_name}</td>
                      <td className="p-2.5 text-slate-500">{u.unit_type || 'Residential'}</td>
                      <td className="p-2.5">
                        <Badge
                          variant={
                            u.status === 'OCCUPIED' ? 'success' : u.status === 'AVAILABLE' ? 'info' : 'warning'
                          }
                        >
                          {u.status || 'AVAILABLE'}
                        </Badge>
                      </td>
                      <td className="p-2.5 text-right font-bold text-slate-900">
                        ₹{Number(u.market_rent).toLocaleString('en-IN')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
