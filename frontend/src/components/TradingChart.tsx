import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Paper,
  Box,
  ToggleButton,
  ToggleButtonGroup,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography
} from '@mui/material';
import axios from 'axios';

interface MarketData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface TradingChartProps {
  symbol: string;
  exchange: string;
}

const TradingChart: React.FC<TradingChartProps> = ({ symbol, exchange }) => {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [timeframe, setTimeframe] = useState('1h');
  const [chartType, setChartType] = useState('line');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMarketData();
  }, [symbol, exchange, timeframe]);

  const fetchMarketData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/v1/market-data/${symbol}`, {
        params: { exchange, timeframe, limit: 100 }
      });
      setMarketData(response.data);
    } catch (error) {
      console.error('Error fetching market data:', error);
    } finally {
      setLoading(false);
    }
  };

  const lineData = {
    labels: marketData.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: `${symbol} Price`,
        data: marketData.map(d => d.close),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `${symbol} (${exchange}) - ${timeframe}`,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
  };

  return (
    <Paper sx={{ p: 2, height: 400 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">{symbol} Chart</Typography>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 80 }}>
            <InputLabel>Timeframe</InputLabel>
            <Select
              value={timeframe}
              label="Timeframe"
              onChange={(e) => setTimeframe(e.target.value)}
            >
              <MenuItem value="1m">1m</MenuItem>
              <MenuItem value="5m">5m</MenuItem>
              <MenuItem value="1h">1h</MenuItem>
              <MenuItem value="1d">1d</MenuItem>
            </Select>
          </FormControl>

          <ToggleButtonGroup
            value={chartType}
            exclusive
            onChange={(e, newType) => newType && setChartType(newType)}
            size="small"
          >
            <ToggleButton value="line">Line</ToggleButton>
            <ToggleButton value="candle">Candle</ToggleButton>
          </ToggleButtonGroup>
        </Box>
      </Box>

      {!loading && marketData.length > 0 && (
        // TODO: Implement real candlestick chart when financial plugin is added
        <Line data={lineData} options={chartOptions} />
      )}

      {loading && <Typography>Loading chart data...</Typography>}
    </Paper>
  );
};

export default TradingChart;
