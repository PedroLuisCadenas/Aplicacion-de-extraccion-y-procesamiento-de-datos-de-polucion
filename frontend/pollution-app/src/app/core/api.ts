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
  providedIn: 'root',
})
export class Api {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  getUserInfo(): Observable<UserInfo> {
    return this.http.get<UserInfo>(`${this.baseUrl}/api/user/info`);
  }

  getLatestDeviceInfo(): Observable<DeviceInfo> {
    return this.http.get<DeviceInfo>(`${this.baseUrl}/api/v1/device/info/latest`);
  }

  getLatestReadings(): Observable<LatestReadings> {
    return this.http.get<LatestReadings>(`${this.baseUrl}/api/v1/device/readings/latest`);
  }

  getReadingsHistory(params: ReadingsHistoryParams, elementId?: string): Observable<ReadingsHistoryPoint[]> {
    const httpParams: Record<string, string | number> = { ...params };
    if (elementId) {
      httpParams['element_id'] = elementId;
    }
    return this.http.get<ReadingsHistoryPoint[]>(`${this.baseUrl}/api/v1/device/readings`, {
      params: httpParams,
    });
  }

  getDeviceElements(): Observable<DeviceElement[]> {
    return this.http.get<DeviceElement[]>(`${this.baseUrl}/api/v1/device/elements`);
  }
}
