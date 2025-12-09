import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, CheckCircle, TrendingUp, Gauge, Clock, Zap, Wrench, ThermometerSun, RotateCw } from 'lucide-react';

/**
 * Main Application Component
 * Manages the entire Smart IIoT Monitoring Dashboard with navigation between
 * machine overview and detailed monitoring views
 */
const SmartIIoTDashboard = () => {
  // State for current view: 'overview' or 'detail'
  const [currentView, setCurrentView] = useState('overview');
  // Currently selected machine for detailed view
  const [selectedMachine, setSelectedMachine] = useState(null);
  // All machines data with their current status
  const [machines, setMachines] = useState([]);
  // Real-time sensor data for selected machine
  const [sensorData, setSensorData] = useState([]);
  // Current failure probability for selected machine
  const [failureProbability, setFailureProbability] = useState(0);

  /**
   * Initialize machines with sample data on component mount
   * In production, this would fetch from your API
   */
  useEffect(() => {
    initializeMachines();
  }, []);

  /**
   * Start real-time monitoring when a machine is selected
   * Simulates continuous sensor data updates
   */
  useEffect(() => {
    if (currentView === 'detail' && selectedMachine) {
      const interval = setInterval(() => {
        updateSensorData();
      }, 2000); // Update every 2 seconds

      return () => clearInterval(interval);
    }
  }, [currentView, selectedMachine]);

  /**
   * Initializes the list of machines being monitored
   * Creates 8 sample machines with varying statuses
   */
  const initializeMachines = () => {
    const machineList = [
      { id: 'M001', name: 'CNC Machine A', type: 'H', status: 'healthy', lastCheck: new Date() },
      { id: 'M002', name: 'Press Machine B', type: 'M', status: 'warning', lastCheck: new Date() },
      { id: 'M003', name: 'Lathe Machine C', type: 'L', status: 'healthy', lastCheck: new Date() },
      { id: 'M004', name: 'Mill Machine D', type: 'H', status: 'critical', lastCheck: new Date() },
      { id: 'M005', name: 'Drill Press E', type: 'M', status: 'healthy', lastCheck: new Date() },
      { id: 'M006', name: 'Grinder F', type: 'L', status: 'warning', lastCheck: new Date() },
      { id: 'M007', name: 'Welder G', type: 'M', status: 'healthy', lastCheck: new Date() },
      { id: 'M008', name: 'Router H', type: 'H', status: 'healthy', lastCheck: new Date() },
    ];
    setMachines(machineList);
  };

  /**
   * Generates realistic sensor readings with slight variations
   * Simulates real-time data from industrial sensors
   */
  const updateSensorData = () => {
    const newDataPoint = {
      timestamp: new Date().toLocaleTimeString(),
      airTemp: 298 + Math.random() * 4,
      processTemp: 308 + Math.random() * 4,
      rotationalSpeed: 1400 + Math.random() * 200,
      torque: 35 + Math.random() * 15,
      toolWear: Math.min(250, (sensorData.length * 2) + Math.random() * 10),
      power: 0, // Will be calculated
    };
    
    // Calculate power from torque and speed
    newDataPoint.power = newDataPoint.torque * (newDataPoint.rotationalSpeed * (2 * Math.PI / 60));
    
    // Calculate failure probability based on sensor values
    const probability = calculateFailureProbability(newDataPoint);
    setFailureProbability(probability);
    
    // Keep last 20 data points for charts
    setSensorData(prev => [...prev.slice(-19), newDataPoint]);
  };

  /**
   * Calculates failure probability based on sensor readings
   * Uses simplified heuristics based on known failure patterns
   * 
   * @param {Object} data - Sensor readings object
   * @returns {number} Failure probability between 0 and 1
   */
  const calculateFailureProbability = (data) => {
    let risk = 0;
    
    // Tool wear factor (0-250 range)
    if (data.toolWear > 200) risk += 0.4;
    else if (data.toolWear > 150) risk += 0.2;
    else if (data.toolWear > 100) risk += 0.1;
    
    // Temperature difference factor
    const tempDiff = data.processTemp - data.airTemp;
    if (tempDiff > 12) risk += 0.3;
    else if (tempDiff > 10) risk += 0.15;
    
    // High torque factor
    if (data.torque > 45) risk += 0.2;
    else if (data.torque > 40) risk += 0.1;
    
    // Speed anomaly
    if (data.rotationalSpeed < 1300 || data.rotationalSpeed > 1700) risk += 0.1;
    
    return Math.min(risk, 0.95);
  };

  /**
   * Handles machine selection and switches to detail view
   * 
   * @param {Object} machine - Selected machine object
   */
  const handleMachineClick = (machine) => {
    setSelectedMachine(machine);
    setSensorData([]);
    setFailureProbability(0);
    setCurrentView('detail');
  };

  /**
   * Returns to overview from detail view
   */
  const handleBackToOverview = () => {
    setCurrentView('overview');
    setSelectedMachine(null);
    setSensorData([]);
  };

  /**
   * Gets appropriate color based on machine status
   * 
   * @param {string} status - Machine status ('healthy', 'warning', 'critical')
   * @returns {string} Tailwind CSS color class
   */
  const getStatusColor = (status) => {
    switch(status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  /**
   * Gets appropriate icon for machine status
   * 
   * @param {string} status - Machine status
   * @returns {JSX.Element} Lucide icon component
   */
  const getStatusIcon = (status) => {
    switch(status) {
      case 'healthy': return <CheckCircle className="w-6 h-6" />;
      case 'warning': return <AlertTriangle className="w-6 h-6" />;
      case 'critical': return <AlertTriangle className="w-6 h-6" />;
      default: return <Activity className="w-6 h-6" />;
    }
  };

  /**
   * Renders the overview page with all machines
   * 
   * @returns {JSX.Element} Overview page component
   */
  const renderOverview = () => (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <Activity className="w-10 h-10 text-blue-400" />
          Smart IIoT Monitoring System
        </h1>
        <p className="text-slate-400">Real-time predictive maintenance monitoring</p>
      </div>

      {/* Status Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Healthy Machines</p>
              <p className="text-3xl font-bold text-green-400">
                {machines.filter(m => m.status === 'healthy').length}
              </p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-400" />
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Warning Status</p>
              <p className="text-3xl font-bold text-yellow-400">
                {machines.filter(m => m.status === 'warning').length}
              </p>
            </div>
            <AlertTriangle className="w-12 h-12 text-yellow-400" />
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Critical Status</p>
              <p className="text-3xl font-bold text-red-400">
                {machines.filter(m => m.status === 'critical').length}
              </p>
            </div>
            <AlertTriangle className="w-12 h-12 text-red-400" />
          </div>
        </div>
      </div>

      {/* Machine Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {machines.map(machine => (
          <div
            key={machine.id}
            onClick={() => handleMachineClick(machine)}
            className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-blue-500 cursor-pointer transition-all hover:scale-105"
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`${getStatusColor(machine.status)} p-3 rounded-lg text-white`}>
                {getStatusIcon(machine.status)}
              </div>
              <span className="text-xs text-slate-400">Type: {machine.type}</span>
            </div>
            
            <h3 className="text-lg font-semibold text-white mb-1">{machine.name}</h3>
            <p className="text-sm text-slate-400 mb-2">ID: {machine.id}</p>
            
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <Clock className="w-4 h-4" />
              <span>Last check: {machine.lastCheck.toLocaleTimeString()}</span>
            </div>
            
            <div className="mt-4 pt-4 border-t border-slate-700">
              <span className={`text-sm font-medium ${
                machine.status === 'healthy' ? 'text-green-400' :
                machine.status === 'warning' ? 'text-yellow-400' :
                'text-red-400'
              }`}>
                {machine.status === 'healthy' ? '✓ Working Fine' :
                 machine.status === 'warning' ? '⚠ Needs Attention' :
                 '⚠ Maintenance Required'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  /**
   * Renders a mini line chart for sensor parameter
   * 
   * @param {Array} data - Array of data points
   * @param {string} param - Parameter name to plot
   * @param {string} color - Line color
   * @returns {JSX.Element} Mini chart component
   */
  const renderMiniChart = (data, param, color) => {
    if (data.length === 0) return null;
    
    const values = data.map(d => d[param]);
    const max = Math.max(...values);
    const min = Math.min(...values);
    const range = max - min || 1;
    
    const points = values.map((val, idx) => {
      const x = (idx / (values.length - 1)) * 100;
      const y = 100 - ((val - min) / range) * 80;
      return `${x},${y}`;
    }).join(' ');

    return (
      <svg viewBox="0 0 100 100" className="w-full h-20" preserveAspectRatio="none">
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          vectorEffect="non-scaling-stroke"
        />
      </svg>
    );
  };

  /**
   * Renders the detail view for a selected machine
   * Shows real-time sensor data and failure probability
   * 
   * @returns {JSX.Element} Detail page component
   */
  const renderDetailView = () => (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      {/* Header with Back Button */}
      <div className="mb-6">
        <button
          onClick={handleBackToOverview}
          className="mb-4 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
        >
          ← Back to Overview
        </button>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              {selectedMachine.name}
            </h1>
            <p className="text-slate-400">Machine ID: {selectedMachine.id} | Type: {selectedMachine.type}</p>
          </div>
          <div className={`${getStatusColor(selectedMachine.status)} px-4 py-2 rounded-lg text-white font-semibold`}>
            {selectedMachine.status.toUpperCase()}
          </div>
        </div>
      </div>

      {/* Failure Probability Gauge */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mb-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Gauge className="w-6 h-6" />
          Real-Time Failure Probability
        </h2>
        
        <div className="flex items-center gap-8">
          <div className="flex-1">
            <div className="relative h-8 bg-slate-700 rounded-full overflow-hidden">
              <div
                className={`absolute h-full transition-all duration-500 ${
                  failureProbability > 0.7 ? 'bg-red-500' :
                  failureProbability > 0.4 ? 'bg-yellow-500' :
                  'bg-green-500'
                }`}
                style={{ width: `${failureProbability * 100}%` }}
              />
            </div>
            <div className="flex justify-between mt-2 text-xs text-slate-400">
              <span>0%</span>
              <span>25%</span>
              <span>50%</span>
              <span>75%</span>
              <span>100%</span>
            </div>
          </div>
          
          <div className="text-right">
            <div className={`text-5xl font-bold ${
              failureProbability > 0.7 ? 'text-red-400' :
              failureProbability > 0.4 ? 'text-yellow-400' :
              'text-green-400'
            }`}>
              {(failureProbability * 100).toFixed(1)}%
            </div>
            <p className="text-slate-400 text-sm mt-1">
              {failureProbability > 0.7 ? 'Critical - Maintenance Required' :
               failureProbability > 0.4 ? 'Warning - Monitor Closely' :
               'Normal - Operating Fine'}
            </p>
          </div>
        </div>
      </div>

      {/* Sensor Parameters Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {/* Air Temperature */}
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm flex items-center gap-2">
              <ThermometerSun className="w-4 h-4" />
              Air Temperature
            </span>
            <span className="text-white font-semibold">
              {sensorData.length > 0 ? sensorData[sensorData.length - 1].airTemp.toFixed(1) : '--'} K
            </span>
          </div>
          {renderMiniChart(sensorData, 'airTemp', '#3b82f6')}
        </div>

        {/* Process Temperature */}
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm flex items-center gap-2">
              <ThermometerSun className="w-4 h-4" />
              Process Temperature
            </span>
            <span className="text-white font-semibold">
              {sensorData.length > 0 ? sensorData[sensorData.length - 1].processTemp.toFixed(1) : '--'} K
            </span>
          </div>
          {renderMiniChart(sensorData, 'processTemp', '#ef4444')}
        </div>

        {/* Rotational Speed */}
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm flex items-center gap-2">
              <RotateCw className="w-4 h-4" />
              Rotational Speed
            </span>
            <span className="text-white font-semibold">
              {sensorData.length > 0 ? sensorData[sensorData.length - 1].rotationalSpeed.toFixed(0) : '--'} RPM
            </span>
          </div>
          {renderMiniChart(sensorData, 'rotationalSpeed', '#10b981')}
        </div>

        {/* Torque */}
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Torque
            </span>
            <span className="text-white font-semibold">
              {sensorData.length > 0 ? sensorData[sensorData.length - 1].torque.toFixed(1) : '--'} Nm
            </span>
          </div>
          {renderMiniChart(sensorData, 'torque', '#f59e0b')}
        </div>

        {/* Tool Wear */}
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm flex items-center gap-2">
              <Wrench className="w-4 h-4" />
              Tool Wear
            </span>
            <span className="text-white font-semibold">
              {sensorData.length > 0 ? sensorData[sensorData.length - 1].toolWear.toFixed(0) : '--'} min
            </span>
          </div>
          {renderMiniChart(sensorData, 'toolWear', '#8b5cf6')}
        </div>

        {/* Power */}
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Power
            </span>
            <span className="text-white font-semibold">
              {sensorData.length > 0 ? sensorData[sensorData.length - 1].power.toFixed(0) : '--'} W
            </span>
          </div>
          {renderMiniChart(sensorData, 'power', '#ec4899')}
        </div>
      </div>

      {/* Data Log */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-semibold text-white mb-4">Recent Data Log</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-2 px-4 text-slate-400 font-medium">Time</th>
                <th className="text-left py-2 px-4 text-slate-400 font-medium">Air Temp</th>
                <th className="text-left py-2 px-4 text-slate-400 font-medium">Process Temp</th>
                <th className="text-left py-2 px-4 text-slate-400 font-medium">Speed</th>
                <th className="text-left py-2 px-4 text-slate-400 font-medium">Torque</th>
                <th className="text-left py-2 px-4 text-slate-400 font-medium">Tool Wear</th>
                <th className="text-left py-2 px-4 text-slate-400 font-medium">Risk</th>
              </tr>
            </thead>
            <tbody>
              {sensorData.slice(-10).reverse().map((data, idx) => (
                <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-2 px-4 text-slate-300">{data.timestamp}</td>
                  <td className="py-2 px-4 text-slate-300">{data.airTemp.toFixed(1)} K</td>
                  <td className="py-2 px-4 text-slate-300">{data.processTemp.toFixed(1)} K</td>
                  <td className="py-2 px-4 text-slate-300">{data.rotationalSpeed.toFixed(0)} RPM</td>
                  <td className="py-2 px-4 text-slate-300">{data.torque.toFixed(1)} Nm</td>
                  <td className="py-2 px-4 text-slate-300">{data.toolWear.toFixed(0)} min</td>
                  <td className="py-2 px-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      calculateFailureProbability(data) > 0.7 ? 'bg-red-500/20 text-red-400' :
                      calculateFailureProbability(data) > 0.4 ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-green-500/20 text-green-400'
                    }`}>
                      {(calculateFailureProbability(data) * 100).toFixed(0)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  return currentView === 'overview' ? renderOverview() : renderDetailView();
};

export default SmartIIoTDashboard;