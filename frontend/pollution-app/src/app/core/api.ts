// Servicio único que centraliza todas las llamadas a la API del backend

import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface DeviceInfo {
  [field: string]: string | number | boolean;
}

export interface UserInfo {
  [field: string]: string | number | boolean;
}

export interface LatestReadings {
  [sensor: string]: number;
}

export interface ReadingsHistoryPoint {
  time: string;
  [sensor: string]: string | number;
}

export interface DeviceElement {
  id: string;
  name: string;
  unit: string;
}

export type ReadingsHistoryParams =
  | { hours: number }
  | { start: string; end?: string };

@Injectable({
  providedIn: 'root', // Esto asegura que la clase Api esté disponible en toda la app
})
export class Api {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl; // http:localhost:8200 (backend FastAPI)

  // Único endpoint interno, trae información del usuario
  getUserInfo(): Observable<UserInfo> {
    return this.http.get<UserInfo>(`${this.baseUrl}/api/user/info`);
  }

  // Trae la información más reciente del dispositivo
  getLatestDeviceInfo(): Observable<DeviceInfo> {
    return this.http.get<DeviceInfo>(`${this.baseUrl}/api/v1/device/info/latest`);
  }

  // Trae la información más reciente de los sensores
  getLatestReadings(): Observable<LatestReadings> {
    return this.http.get<LatestReadings>(`${this.baseUrl}/api/v1/device/readings/latest`);
  }

  // Trae el historial de lecturas de los sensores
  getReadingsHistory(params: ReadingsHistoryParams, elementId?: string): Observable<ReadingsHistoryPoint[]> {
    const httpParams: Record<string, string | number> = { ...params };
    if (elementId) {
      httpParams['element_id'] = elementId;
    }
    return this.http.get<ReadingsHistoryPoint[]>(`${this.baseUrl}/api/v1/device/readings`, {
      params: httpParams,
    });
  }

  // Trae la lista de elementos del dispositivo
  getDeviceElements(): Observable<DeviceElement[]> {
    return this.http.get<DeviceElement[]>(`${this.baseUrl}/api/v1/device/elements`);
  }

  // Lanza el backfill del histórico (endpoint interno, ejecuta backfill.py en el backend)
  runBackfill(days: number): Observable<{ status: string; days: number }> {
    return this.http.post<{ status: string; days: number }>(
      `${this.baseUrl}/api/backfill`,
      null,
      { params: { days } },
    );
  }
}
