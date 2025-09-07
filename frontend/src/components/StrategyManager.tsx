import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Switch,
  FormControlLabel,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  IconButton
} from '@mui/material';
import { Edit, Delete, Add } from '@mui/icons-material';
import axios from 'axios';

interface Strategy {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  parameters: string;
  performance_metrics: string;
  created_at: string;
  updated_at: string;
}

const StrategyManager: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [newStrategy, setNewStrategy] = useState({
    name: '',
    description: '',
    parameters: '{}'
  });

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      const response = await axios.get('/api/v1/strategies');
      setStrategies(response.data);
    } catch (error) {
      console.error('Error fetching strategies:', error);
    }
  };

  const toggleStrategy = async (id: number, isActive: boolean) => {
    try {
      await axios.patch(`/api/v1/strategies/${id}`, {
        is_active: !isActive
      });
      fetchStrategies();
    } catch (error) {
      console.error('Error updating strategy:', error);
    }
  };

  const handleSaveStrategy = async () => {
    try {
      if (selectedStrategy) {
        await axios.put(`/api/v1/strategies/${selectedStrategy.id}`, {
          ...newStrategy,
          parameters: newStrategy.parameters
        });
      } else {
        await axios.post('/api/v1/strategies', {
          ...newStrategy,
          parameters: newStrategy.parameters
        });
      }
      setEditDialog(false);
      setSelectedStrategy(null);
      setNewStrategy({ name: '', description: '', parameters: '{}' });
      fetchStrategies();
    } catch (error) {
      console.error('Error saving strategy:', error);
    }
  };

  const handleEditStrategy = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
    setNewStrategy({
      name: strategy.name,
      description: strategy.description,
      parameters: strategy.parameters
    });
    setEditDialog(true);
  };

  const handleDeleteStrategy = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this strategy?')) {
      try {
        await axios.delete(`/api/v1/strategies/${id}`);
        fetchStrategies();
      } catch (error) {
        console.error('Error deleting strategy:', error);
      }
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Strategy Management</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => {
            setSelectedStrategy(null);
            setNewStrategy({ name: '', description: '', parameters: '{}' });
            setEditDialog(true);
          }}
        >
          Add Strategy
        </Button>
      </Box>

      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Performance</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {strategies.map((strategy) => (
              <TableRow key={strategy.id}>
                <TableCell>{strategy.name}</TableCell>
                <TableCell>{strategy.description}</TableCell>
                <TableCell>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={strategy.is_active}
                        onChange={() => toggleStrategy(strategy.id, strategy.is_active)}
                      />
                    }
                    label={strategy.is_active ? 'Active' : 'Inactive'}
                  />
                </TableCell>
                <TableCell>
                  {strategy.performance_metrics && (
                    <Chip label="View Metrics" variant="outlined" size="small" />
                  )}
                </TableCell>
                <TableCell>
                  <IconButton onClick={() => handleEditStrategy(strategy)} size="small">
                    <Edit />
                  </IconButton>
                  <IconButton onClick={() => handleDeleteStrategy(strategy.id)} size="small">
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Edit Strategy Dialog */}
      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedStrategy ? 'Edit Strategy' : 'Add New Strategy'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Strategy Name"
            fullWidth
            variant="outlined"
            value={newStrategy.name}
            onChange={(e) => setNewStrategy({ ...newStrategy, name: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newStrategy.description}
            onChange={(e) => setNewStrategy({ ...newStrategy, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Parameters (JSON)"
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            value={newStrategy.parameters}
            onChange={(e) => setNewStrategy({ ...newStrategy, parameters: e.target.value })}
            helperText="Enter strategy parameters in JSON format"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveStrategy} variant="contained">
            {selectedStrategy ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default StrategyManager;
