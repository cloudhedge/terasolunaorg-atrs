/**
 * Tests for constants.ts — reference data integrity.
 */

import { describe, it, expect } from "vitest";
import {
  AIRPORTS,
  AIRPORT_CODES,
  FARE_TYPES,
  BOARDING_CLASSES,
  API_BASE_URL,
  CHARACTER_LIMIT,
  REQUEST_TIMEOUT,
} from "../constants.js";

describe("constants", () => {
  describe("AIRPORTS", () => {
    it("should contain exactly 50 airports", () => {
      expect(AIRPORTS).toHaveLength(50);
    });

    it("should have unique 3-letter codes", () => {
      const codes = AIRPORTS.map((a) => a.code);
      const unique = new Set(codes);
      expect(unique.size).toBe(50);
      codes.forEach((c) => expect(c).toHaveLength(3));
    });

    it("should have non-empty names", () => {
      AIRPORTS.forEach((a) => {
        expect(a.name.length).toBeGreaterThan(0);
      });
    });

    it("should include major airports (HND, NRT, KIX, SPK, FUK)", () => {
      const codes = AIRPORTS.map((a) => a.code);
      expect(codes).toContain("HND");
      expect(codes).toContain("NRT");
      expect(codes).toContain("KIX");
      expect(codes).toContain("SPK");
      expect(codes).toContain("FUK");
    });
  });

  describe("AIRPORT_CODES", () => {
    it("should be a Set with 50 entries", () => {
      expect(AIRPORT_CODES).toBeInstanceOf(Set);
      expect(AIRPORT_CODES.size).toBe(50);
    });

    it("should validate known codes", () => {
      expect(AIRPORT_CODES.has("HND")).toBe(true);
      expect(AIRPORT_CODES.has("XXX")).toBe(false);
    });
  });

  describe("FARE_TYPES", () => {
    it("should contain exactly 10 fare types", () => {
      expect(FARE_TYPES).toHaveLength(10);
    });

    it("should have unique codes", () => {
      const codes = FARE_TYPES.map((f) => f.code);
      expect(new Set(codes).size).toBe(10);
    });

    it("should include all expected codes", () => {
      const codes = FARE_TYPES.map((f) => f.code);
      const expected = ["OW", "RT", "RD1", "RD7", "ED", "LD", "GD", "SOW", "SRT", "SRD"];
      expected.forEach((c) => expect(codes).toContain(c));
    });

    it("should have valid discount rates (0-100)", () => {
      FARE_TYPES.forEach((f) => {
        expect(f.discountRate).toBeGreaterThanOrEqual(0);
        expect(f.discountRate).toBeLessThanOrEqual(100);
      });
    });

    it("should have positive min passengers", () => {
      FARE_TYPES.forEach((f) => {
        expect(f.minPassengers).toBeGreaterThanOrEqual(1);
      });
    });

    it("should require 3+ passengers for group discount", () => {
      const gd = FARE_TYPES.find((f) => f.code === "GD");
      expect(gd?.minPassengers).toBe(3);
    });
  });

  describe("BOARDING_CLASSES", () => {
    it("should contain Normal and Special", () => {
      expect(BOARDING_CLASSES).toHaveLength(2);
      expect(BOARDING_CLASSES[0].code).toBe("N");
      expect(BOARDING_CLASSES[1].code).toBe("S");
    });

    it("should have 0 extra charge for Normal, 5000 for Special", () => {
      expect(BOARDING_CLASSES[0].extraCharge).toBe(0);
      expect(BOARDING_CLASSES[1].extraCharge).toBe(5000);
    });
  });

  describe("config values", () => {
    it("should have sensible defaults", () => {
      expect(API_BASE_URL).toContain("/api/v1");
      expect(CHARACTER_LIMIT).toBe(25000);
      expect(REQUEST_TIMEOUT).toBe(30000);
    });
  });
});
