import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Api, DeviceElement, DeviceInfo, LatestReadings } from '../../core/api';

const KEY_SENSOR_NAMES = ['Heat Index', 'Humidity Index', 'NO2 GCC', 'Pressure', 'Temp', 'Temp ext'];

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})

export class Dashboard implements OnInit {
  private readonly api = inject(Api);

  protected readonly deviceElements = signal<DeviceElement[]>([]);
  protected readonly latestReadings = signal<LatestReadings>({});
  protected readonly deviceInfo = signal<DeviceInfo | null>(null);
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);

  ngOnInit(): void {
    this.api.getDeviceElements().subscribe({
      next: (elements) => this.deviceElements.set(elements),
      error: () => this.error.set('No se han podido cargar los sensores del dispositivo.'),
    });
    this.api.getLatestReadings().subscribe({
      next: (readings) => this.latestReadings.set(readings),
      error: () => this.error.set('No se han podido cargar los datos del dispositivo.'),
    });
    this.api.getLatestDeviceInfo().subscribe({
      next: (info) => this.deviceInfo.set(info),
      error: () => this.error.set('No se ha podido cargar la información del dispositivo.'),
    });

  }

  protected readonly cardKPI = computed(() => {
    const readings = this.latestReadings();
    const elements = this.deviceElements();
    const kpiElements = elements.filter((element) => KEY_SENSOR_NAMES.includes(element.name));
    return kpiElements.map((element) => ({
      id: element.id,
      name: element.name,
      unit: element.unit,
      value: readings[element.id] ?? null,
    }));
  });



}
