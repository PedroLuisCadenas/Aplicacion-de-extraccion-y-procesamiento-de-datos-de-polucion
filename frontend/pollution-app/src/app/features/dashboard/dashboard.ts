import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { ChartConfiguration, ChartData } from 'chart.js';
import 'chartjs-adapter-date-fns';
import { RouterLink } from '@angular/router';
import { BaseChartDirective } from 'ng2-charts';
import { Api, DeviceElement, DeviceInfo, LatestReadings, ReadingsHistoryPoint } from '../../core/api';

const KEY_SENSOR_NAMES = ['Heat Index', 'Humidity ext', 'NO2 GCc', 'Temp', 'Temp ext'];

function round2(value: number): number {
  return Math.round(value * 100) / 100;
}

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink, BaseChartDirective],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})

export class Dashboard implements OnInit {
  private readonly api = inject(Api);

  protected readonly deviceElements = signal<DeviceElement[]>([]);
  protected readonly latestReadings = signal<LatestReadings>({});
  protected readonly deviceInfo = signal<DeviceInfo | null>(null);
  protected readonly historyRows = signal<ReadingsHistoryPoint[]>([]);
  protected readonly miniChartsOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: 'time',
        time: { unit: 'day', displayFormats: { day: 'd' }, tooltipFormat: 'dd/MM/yyyy HH:mm' },
        ticks: { autoSkip: true, maxRotation: 0, font: { size: 10 } },
        grid: { display: false },
      },
      y: {
        ticks: { font: { size: 10 } },
        grid: { color: '#eef1f0' },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
    },
  };
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
    this.api.getReadingsHistory({ hours: 24 * 7 }).subscribe({
      next: (history) => this.historyRows.set(history),
      error: () => this.error.set('No se han podido cargar los datos históricos del dispositivo.'),
    });

  }

  protected readonly cardKPI = computed(() => {
    const readings = this.latestReadings();
    const elements = this.deviceElements();
    const kpiElements = elements.filter((element) => KEY_SENSOR_NAMES.includes(element.name));
    return kpiElements.map((element) => {
      const points = this.historyRows()
        .filter((row) => row[element.id] != null)
        .map((row) => ({ x: new Date(row.time).getTime(), y: row[element.id] as number }));
      const values = points.map((point) => point.y);
      return {
        id: element.id,
        name: element.name,
        unit: element.unit,
        value: readings[element.id] ?? null,
        max: values.length ? round2(Math.max(...values)) : null,
        min: values.length ? round2(Math.min(...values)) : null,
        chartData: {
          datasets: [
            {
              data: points,
              borderColor: '#1b3a2f',
              backgroundColor: 'rgba(27, 58, 47, 0.12)',
              pointRadius: 0,
              tension: 0.3,
              fill: true,
            },
          ],
        } as ChartData<'line'>,
      };
    });
  });
}