import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import { Line } from 'react-chartjs-2';
import axios from 'axios';

interface PortfolioSummary {
  portfolio_id: number;
  total_value: number;
  cash_balance: number;
  market_value: number;
  unrealized_pnl: number;
  positions_count: number;
  updated_at: string;
}

interface Position {
  id: number;
  symbol: string;
  exchange: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  pnl_percentage: number;
}

interface Trade {
  id: number;
  symbol: string;
  exchange: string;
  side: string;
  quantity: number;
  price: number;
  commission: number;
  strategy: string;
  executed_at: string;
}

const Dashboard: React.FC = () => {
  const [portfolioSummary, setPortfolioSummary] = useState<PortfolioSummary | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [summaryRes, positionsRes, tradesRes] = await Promise.all([
        axios.get('/api/v1/portfolio/summary'),
        axios.get('/api/v1/portfolio/positions'),
        axios.get('/api/v1/portfolio/trades?limit=10')
      ]);
      
      setPortfolioSummary(summaryRes.data);
      setPositions(positionsRes.data);
      setRecentTrades(tradesRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('he-IL', {
      style: 'currency',
      currency: 'ILS'
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (loading) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom>
        AI Trading Dashboard
      </Typography>
      
      {/* Portfolio Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Portfolio Value
              </Typography>
              <Typography variant="h5">
                {portfolioSummary ? formatCurrency(portfolioSummary.total_value) : '-'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Cash Balance
              </Typography>
              <Typography variant="h5">
                {portfolioSummary ? formatCurrency(portfolioSummary.cash_balance) : '-'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Market Value
              </Typography>
              <Typography variant="h5">
                {portfolioSummary ? formatCurrency(portfolioSummary.market_value) : '-'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Unrealized P&L
              </Typography>
              <Typography 
                variant="h5" 
                color={portfolioSummary && portfolioSummary.unrealized_pnl >= 0 ? 'success.main' : 'error.main'}
              >
                {portfolioSummary ? formatCurrency(portfolioSummary.unrealized_pnl) : '-'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Current Positions */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Current Positions
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Symbol</TableCell>
                    <TableCell>Exchange</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                    <TableCell align="right">Avg Price</TableCell>
                    <TableCell align="right">Current Price</TableCell>
                    <TableCell align="right">Market Value</TableCell>
                    <TableCell align="right">P&L</TableCell>
                    <TableCell align="right">P&L %</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {positions.map((position) => (
                    <TableRow key={position.id}>
                      <TableCell>{position.symbol}</TableCell>
                      <TableCell>{position.exchange}</TableCell>
                      <TableCell align="right">{position.quantity}</TableCell>
                      <TableCell align="right">{formatCurrency(position.avg_price)}</TableCell>
                      <TableCell align="right">{formatCurrency(position.current_price)}</TableCell>
                      <TableCell align="right">{formatCurrency(position.market_value)}</TableCell>
                      <TableCell 
                        align="right"
                        sx={{ color: position.unrealized_pnl >= 0 ? 'success.main' : 'error.main' }}
                      >
                        {formatCurrency(position.unrealized_pnl)}
                      </TableCell>
                      <TableCell 
                        align="right"
                        sx={{ color: position.pnl_percentage >= 0 ? 'success.main' : 'error.main' }}
                      >
                        {formatPercentage(position.pnl_percentage)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Recent Trades */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Trades
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Symbol</TableCell>
                    <TableCell>Side</TableCell>
                    <TableCell align="right">Qty</TableCell>
                    <TableCell align="right">Price</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentTrades.map((trade) => (
                    <TableRow key={trade.id}>
                      <TableCell>{trade.symbol}</TableCell>
                      <TableCell>
                        <Chip 
                          label={trade.side} 
                          color={trade.side === 'BUY' ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">{trade.quantity}</TableCell>
                      <TableCell align="right">{formatCurrency(trade.price)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
