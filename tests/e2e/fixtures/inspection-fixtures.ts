/**
 * Inspection fixtures for E2E tests.
 * Provides functions to create and delete test inspection entities.
 */

import { APIRequestContext, request } from '@playwright/test';

// Test data constants
export const TEST_INSPECTOR = {
  id: 'INS001',
  name: 'John Doe',
  email: 'john.doe@checkmate-virtue.com',
  phone: '+1-555-0123'
};

export const TEST_VEHICLE = {
  vin: '1HGBH41JXMN109186',
  year: '2020',
  make: 'Honda',
  model: 'Civic',
  trim: 'EX',
  engine: '1.5L Turbo',
  transmission: 'CVT',
  body_style: 'Sedan',
  fuel_type: 'Gasoline',
  drivetrain: 'FWD'
};

export const TEST_INSPECTION_TITLE = 'Comprehensive Vehicle Inspection';

// Base URL for API requests
const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:8000';

// API client for test operations
class TestAPIClient {
  private context: APIRequestContext;

  constructor(context: APIRequestContext) {
    this.context = context;
  }

  /**
   * Reset test data to initial state
   */
  async resetTestData(): Promise<void> {
    try {
      const response = await this.context.post(`${BASE_URL}/test/reset`);
      if (response.ok()) {
        console.log('✅ Test data reset successfully');
      } else {
        console.warn('⚠️ Test data reset failed:', await response.text());
      }
    } catch (error) {
      console.warn('⚠️ Test data reset failed:', error);
    }
  }

  /**
   * Seed test data with multiple inspections
   */
  async seedTestData(): Promise<string[]> {
    try {
      const response = await this.context.post(`${BASE_URL}/test/seed`);
      if (response.ok()) {
        const data = await response.json();
        console.log('✅ Test data seeded successfully:', data.inspection_ids);
        return data.inspection_ids;
      } else {
        console.warn('⚠️ Test data seeding failed:', await response.text());
        return [];
      }
    } catch (error) {
      console.warn('⚠️ Test data seeding failed:', error);
      return [];
    }
  }

  /**
   * Create a single test inspection
   */
  async createTestInspection(): Promise<string | null> {
    try {
      const response = await this.context.post(`${BASE_URL}/test/inspection`);
      if (response.ok()) {
        const data = await response.json();
        console.log('✅ Test inspection created:', data.inspection.id);
        return data.inspection.id;
      } else {
        console.warn('⚠️ Test inspection creation failed:', await response.text());
        return null;
      }
    } catch (error) {
      console.warn('⚠️ Test inspection creation failed:', error);
      return null;
    }
  }

  /**
   * Delete a specific test inspection
   */
  async deleteTestInspection(inspectionId: string): Promise<boolean> {
    try {
      const response = await this.context.delete(`${BASE_URL}/test/inspections/${inspectionId}`);
      if (response.ok()) {
        console.log('✅ Test inspection deleted:', inspectionId);
        return true;
      } else {
        console.warn('⚠️ Test inspection deletion failed:', await response.text());
        return false;
      }
    } catch (error) {
      console.warn('⚠️ Test inspection deletion failed:', error);
      return false;
    }
  }

  /**
   * Clear all test inspections
   */
  async clearAllTestInspections(): Promise<void> {
    try {
      const response = await this.context.delete(`${BASE_URL}/test/inspections`);
      if (response.ok()) {
        console.log('✅ All test inspections cleared');
      } else {
        console.warn('⚠️ Clear test inspections failed:', await response.text());
      }
    } catch (error) {
      console.warn('⚠️ Clear test inspections failed:', error);
    }
  }

  /**
   * Get all test inspections
   */
  async getTestInspections(): Promise<any[]> {
    try {
      const response = await this.context.get(`${BASE_URL}/test/inspections`);
      if (response.ok()) {
        const data = await response.json();
        return data.inspections || [];
      } else {
        console.warn('⚠️ Get test inspections failed:', await response.text());
        return [];
      }
    } catch (error) {
      console.warn('⚠️ Get test inspections failed:', error);
      return [];
    }
  }

  /**
   * Check test mode status
   */
  async getTestModeStatus(): Promise<any> {
    try {
      const response = await this.context.get(`${BASE_URL}/test/status`);
      if (response.ok()) {
        return await response.json();
      } else {
        console.warn('⚠️ Get test mode status failed:', await response.text());
        return null;
      }
    } catch (error) {
      console.warn('⚠️ Get test mode status failed:', error);
      return null;
    }
  }
}

// Fixture functions
export class InspectionFixtures {
  private apiClient: TestAPIClient;

  constructor(context: APIRequestContext) {
    this.apiClient = new TestAPIClient(context);
  }

  /**
   * Setup test environment - reset data and create initial inspection
   */
  async setupTestEnvironment(): Promise<string | null> {
    console.log('🔧 Setting up test environment...');
    
    // Reset test data
    await this.apiClient.resetTestData();
    
    // Create a fresh test inspection
    const inspectionId = await this.apiClient.createTestInspection();
    
    if (inspectionId) {
      console.log('✅ Test environment setup complete');
    } else {
      console.warn('⚠️ Test environment setup incomplete');
    }
    
    return inspectionId;
  }

  /**
   * Cleanup test environment - delete all test data
   */
  async cleanupTestEnvironment(): Promise<void> {
    console.log('🧹 Cleaning up test environment...');
    
    // Clear all test inspections
    await this.apiClient.clearAllTestInspections();
    
    console.log('✅ Test environment cleanup complete');
  }

  /**
   * Create a test inspection for a specific test
   */
  async createTestInspectionForTest(testName: string): Promise<string | null> {
    console.log(`🔧 Creating test inspection for: ${testName}`);
    
    const inspectionId = await this.apiClient.createTestInspection();
    
    if (inspectionId) {
      console.log(`✅ Test inspection created for ${testName}: ${inspectionId}`);
    } else {
      console.warn(`⚠️ Failed to create test inspection for ${testName}`);
    }
    
    return inspectionId;
  }

  /**
   * Delete a test inspection after a specific test
   */
  async deleteTestInspectionAfterTest(inspectionId: string, testName: string): Promise<void> {
    console.log(`🧹 Deleting test inspection for: ${testName}`);
    
    const success = await this.apiClient.deleteTestInspection(inspectionId);
    
    if (success) {
      console.log(`✅ Test inspection deleted for ${testName}: ${inspectionId}`);
    } else {
      console.warn(`⚠️ Failed to delete test inspection for ${testName}: ${inspectionId}`);
    }
  }

  /**
   * Verify test mode is enabled
   */
  async verifyTestMode(): Promise<boolean> {
    const status = await this.apiClient.getTestModeStatus();
    
    if (status && status.test_mode_enabled) {
      console.log('✅ Test mode is enabled');
      return true;
    } else {
      console.warn('⚠️ Test mode is not enabled:', status);
      return false;
    }
  }

  /**
   * Get test inspector data
   */
  getTestInspector() {
    return TEST_INSPECTOR;
  }

  /**
   * Get test vehicle data
   */
  getTestVehicle() {
    return TEST_VEHICLE;
  }

  /**
   * Get test inspection title
   */
  getTestInspectionTitle() {
    return TEST_INSPECTION_TITLE;
  }
}

// Helper function to create fixtures instance
export function createInspectionFixtures(context: APIRequestContext): InspectionFixtures {
  return new InspectionFixtures(context);
}

// Export test data for direct use
export {
  TEST_INSPECTOR,
  TEST_VEHICLE,
  TEST_INSPECTION_TITLE
};
