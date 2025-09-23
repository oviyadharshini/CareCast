"""
Staff Allocation Optimization using Linear Programming (PuLP)
Optimizes hospital staff allocation based on predicted demand and constraints.
"""

import pulp
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd

class StaffOptimizer:
    def __init__(self):
        self.staff_types = ['Nurses', 'Doctors', 'Support_Staff']
        self.shifts = ['Morning', 'Evening', 'Night']
        self.base_costs = {
            'Nurses': {'Morning': 25, 'Evening': 28, 'Night': 32},
            'Doctors': {'Morning': 80, 'Evening': 85, 'Night': 95},
            'Support_Staff': {'Morning': 18, 'Evening': 20, 'Night': 25}
        }
        
    def optimize_allocation(self, current_staff: Dict[str, Dict[str, int]], 
                          predicted_demand: Dict[str, float], 
                          constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optimize staff allocation using linear programming
        
        Args:
            current_staff: Current staff allocation by type and shift
            predicted_demand: Predicted resource demand
            constraints: Additional constraints (budget, min/max staff, etc.)
            
        Returns:
            Optimization result with recommended allocation
        """
        
        # Create optimization problem
        prob = pulp.LpProblem("Hospital_Staff_Optimization", pulp.LpMinimize)
        
        # Decision variables: staff count for each type and shift
        staff_vars = {}
        for staff_type in self.staff_types:
            staff_vars[staff_type] = {}
            for shift in self.shifts:
                var_name = f"{staff_type}_{shift}"
                staff_vars[staff_type][shift] = pulp.LpVariable(
                    var_name, 
                    lowBound=1,  # Minimum 1 staff per type per shift
                    upBound=50,  # Maximum 50 staff per type per shift
                    cat='Integer'
                )
        
        # Objective function: minimize total cost
        total_cost = 0
        for staff_type in self.staff_types:
            for shift in self.shifts:
                cost_per_person = self.base_costs[staff_type][shift]
                total_cost += cost_per_person * staff_vars[staff_type][shift]
        
        prob += total_cost, "Total_Staff_Cost"
        
        # Constraints
        self._add_demand_constraints(prob, staff_vars, predicted_demand)
        self._add_operational_constraints(prob, staff_vars, current_staff)
        self._add_custom_constraints(prob, staff_vars, constraints)
        
        # Solve optimization problem
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        
        # Extract results
        if prob.status == pulp.LpStatusOptimal:
            result = self._extract_solution(staff_vars, prob)
            result['status'] = 'optimal'
        else:
            result = self._fallback_solution(current_staff, predicted_demand)
            result['status'] = 'fallback'
        
        result['optimization_timestamp'] = datetime.now().isoformat()
        return result
    
    def _add_demand_constraints(self, prob, staff_vars, predicted_demand):
        """Add constraints based on predicted demand"""
        
        # Total nurse requirement based on bed occupancy prediction
        if 'bed_occupancy' in predicted_demand:
            bed_occupancy = predicted_demand['bed_occupancy']
            
            # Nurse-to-patient ratios: Morning 1:6, Evening 1:8, Night 1:12
            nurse_ratios = {'Morning': 6, 'Evening': 8, 'Night': 12}
            
            for shift in self.shifts:
                min_nurses = max(3, int(bed_occupancy / nurse_ratios[shift]))
                prob += staff_vars['Nurses'][shift] >= min_nurses, f"Min_Nurses_{shift}"
        
        # Doctor requirements based on admissions
        if 'admissions' in predicted_demand:
            admissions = predicted_demand['admissions']
            
            # Higher admissions require more doctors
            if admissions > 12:  # High admission rate
                prob += staff_vars['Doctors']['Morning'] >= 12, "High_Admission_Doctors_Morning"
                prob += staff_vars['Doctors']['Evening'] >= 10, "High_Admission_Doctors_Evening"
            elif admissions < 5:  # Low admission rate
                prob += staff_vars['Doctors']['Morning'] >= 8, "Low_Admission_Doctors_Morning"
                prob += staff_vars['Doctors']['Evening'] >= 6, "Low_Admission_Doctors_Evening"
        
        # Support staff based on overall activity
        total_activity = sum([predicted_demand.get(key, 0) for key in ['admissions', 'bed_occupancy']])
        if total_activity > 200:  # High activity
            for shift in ['Morning', 'Evening']:
                prob += staff_vars['Support_Staff'][shift] >= 8, f"High_Activity_Support_{shift}"
    
    def _add_operational_constraints(self, prob, staff_vars, current_staff):
        """Add operational constraints"""
        
        # Limit changes from current allocation (stability constraint)
        for staff_type in self.staff_types:
            if staff_type in current_staff:
                for shift in self.shifts:
                    if shift in current_staff[staff_type]:
                        current_count = current_staff[staff_type][shift]
                        
                        # Don't change by more than ±30%
                        max_change = max(2, int(current_count * 0.3))
                        
                        prob += (staff_vars[staff_type][shift] >= 
                                current_count - max_change), f"Min_Change_{staff_type}_{shift}"
                        prob += (staff_vars[staff_type][shift] <= 
                                current_count + max_change), f"Max_Change_{staff_type}_{shift}"
        
        # Minimum coverage constraints
        prob += staff_vars['Doctors']['Night'] >= 5, "Min_Night_Doctors"
        prob += staff_vars['Nurses']['Night'] >= 10, "Min_Night_Nurses"
        
        # Weekend requirements (simplified - assume current is weekend if high demand)
        total_current = sum([sum(shifts.values()) for shifts in current_staff.values() if isinstance(shifts, dict)])
        if total_current > 80:  # High current staffing suggests weekend
            for staff_type in ['Nurses', 'Doctors']:
                prob += (staff_vars[staff_type]['Morning'] + 
                        staff_vars[staff_type]['Evening'] >= 
                        int(sum([current_staff.get(staff_type, {}).get(s, 5) for s in ['Morning', 'Evening']]) * 0.9)), f"Weekend_{staff_type}"
    
    def _add_custom_constraints(self, prob, staff_vars, constraints):
        """Add custom constraints provided by user"""
        if not constraints:
            return
        
        # Budget constraint
        if 'max_budget' in constraints:
            max_budget = constraints['max_budget']
            total_cost = 0
            for staff_type in self.staff_types:
                for shift in self.shifts:
                    cost_per_person = self.base_costs[staff_type][shift]
                    total_cost += cost_per_person * staff_vars[staff_type][shift]
            
            prob += total_cost <= max_budget, "Budget_Constraint"
        
        # Minimum staff constraints
        if 'min_total_staff' in constraints:
            total_staff = 0
            for staff_type in self.staff_types:
                for shift in self.shifts:
                    total_staff += staff_vars[staff_type][shift]
            
            prob += total_staff >= constraints['min_total_staff'], "Min_Total_Staff"
        
        # Maximum staff constraints
        if 'max_total_staff' in constraints:
            total_staff = 0
            for staff_type in self.staff_types:
                for shift in self.shifts:
                    total_staff += staff_vars[staff_type][shift]
            
            prob += total_staff <= constraints['max_total_staff'], "Max_Total_Staff"
    
    def _extract_solution(self, staff_vars, prob):
        """Extract optimization solution"""
        optimized_allocation = {}
        total_cost = 0
        
        for staff_type in self.staff_types:
            optimized_allocation[staff_type] = {}
            for shift in self.shifts:
                count = int(pulp.value(staff_vars[staff_type][shift]))
                optimized_allocation[staff_type][shift] = count
                total_cost += count * self.base_costs[staff_type][shift]
        
        return {
            'optimized_allocation': optimized_allocation,
            'total_cost': total_cost,
            'objective_value': pulp.value(prob.objective),
            'solver_status': pulp.LpStatus[prob.status],
            'cost_breakdown': self._calculate_cost_breakdown(optimized_allocation),
            'efficiency_metrics': self._calculate_efficiency_metrics(optimized_allocation)
        }
    
    def _fallback_solution(self, current_staff, predicted_demand):
        """Provide fallback solution when optimization fails"""
        optimized_allocation = {}
        
        # Simple heuristic adjustments
        for staff_type in self.staff_types:
            optimized_allocation[staff_type] = {}
            
            for shift in self.shifts:
                current_count = current_staff.get(staff_type, {}).get(shift, 5)
                
                # Simple adjustment based on demand
                adjustment = 0
                if 'admissions' in predicted_demand:
                    if predicted_demand['admissions'] > 10:
                        adjustment = 2 if shift in ['Morning', 'Evening'] else 1
                    elif predicted_demand['admissions'] < 5:
                        adjustment = -1
                
                if 'bed_occupancy' in predicted_demand:
                    if predicted_demand['bed_occupancy'] > 200:
                        adjustment += 1
                
                optimized_allocation[staff_type][shift] = max(1, current_count + adjustment)
        
        total_cost = sum([
            count * self.base_costs[staff_type][shift]
            for staff_type in optimized_allocation
            for shift, count in optimized_allocation[staff_type].items()
        ])
        
        return {
            'optimized_allocation': optimized_allocation,
            'total_cost': total_cost,
            'objective_value': total_cost,
            'solver_status': 'heuristic_fallback',
            'cost_breakdown': self._calculate_cost_breakdown(optimized_allocation),
            'efficiency_metrics': self._calculate_efficiency_metrics(optimized_allocation)
        }
    
    def _calculate_cost_breakdown(self, allocation):
        """Calculate detailed cost breakdown"""
        breakdown = {}
        
        for staff_type in allocation:
            breakdown[staff_type] = {}
            total_type_cost = 0
            
            for shift, count in allocation[staff_type].items():
                shift_cost = count * self.base_costs[staff_type][shift]
                breakdown[staff_type][shift] = {
                    'count': count,
                    'rate': self.base_costs[staff_type][shift],
                    'cost': shift_cost
                }
                total_type_cost += shift_cost
            
            breakdown[staff_type]['total'] = total_type_cost
        
        return breakdown
    
    def _calculate_efficiency_metrics(self, allocation):
        """Calculate efficiency metrics"""
        total_staff = sum([
            count for staff_type in allocation 
            for count in allocation[staff_type].values()
        ])
        
        total_cost = sum([
            count * self.base_costs[staff_type][shift]
            for staff_type in allocation
            for shift, count in allocation[staff_type].items()
        ])
        
        return {
            'total_staff': total_staff,
            'average_cost_per_staff': round(total_cost / max(1, total_staff), 2),
            'staff_distribution': {
                staff_type: sum(allocation[staff_type].values())
                for staff_type in allocation
            },
            'shift_coverage': {
                shift: sum([allocation[staff_type][shift] for staff_type in allocation])
                for shift in self.shifts
            }
        }
    
    def generate_recommendations(self, current_allocation, optimized_allocation):
        """Generate human-readable recommendations"""
        recommendations = []
        
        for staff_type in self.staff_types:
            for shift in self.shifts:
                current = current_allocation.get(staff_type, {}).get(shift, 0)
                optimized = optimized_allocation[staff_type][shift]
                
                if optimized > current:
                    recommendations.append(
                        f"Increase {staff_type} for {shift} shift: {current} → {optimized} (+{optimized - current})"
                    )
                elif optimized < current:
                    recommendations.append(
                        f"Decrease {staff_type} for {shift} shift: {current} → {optimized} ({optimized - current})"
                    )
        
        if not recommendations:
            recommendations.append("Current staff allocation is optimal")
        
        return recommendations

if __name__ == "__main__":
    # Example usage
    optimizer = StaffOptimizer()
    
    # Sample current staff allocation
    current_staff = {
        'Nurses': {'Morning': 20, 'Evening': 15, 'Night': 12},
        'Doctors': {'Morning': 12, 'Evening': 10, 'Night': 6},
        'Support_Staff': {'Morning': 8, 'Evening': 6, 'Night': 4}
    }
    
    # Sample predicted demand
    predicted_demand = {
        'admissions': 14,
        'bed_occupancy': 180,
        'oxygen_level': 1200
    }
    
    # Sample constraints
    constraints = {
        'max_budget': 15000,
        'min_total_staff': 60
    }
    
    result = optimizer.optimize_allocation(current_staff, predicted_demand, constraints)
    
    print("Optimization Result:")
    print(f"Status: {result['status']}")
    print(f"Total Cost: ${result['total_cost']:,.2f}")
    print("\nOptimized Allocation:")
    
    for staff_type, shifts in result['optimized_allocation'].items():
        print(f"{staff_type}: {shifts}")
    
    recommendations = optimizer.generate_recommendations(current_staff, result['optimized_allocation'])
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"- {rec}")