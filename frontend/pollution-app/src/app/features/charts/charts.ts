import { Component, inject, OnInit, signal } from '@angular/core';
import { ChartConfiguration, ChartData } from 'chart.js';
import 'chartjs-adapter-date-fns';
import { Api, DeviceElement } from '../../core/api';
import { FormsModule } from '@angular/forms';
import { BaseChartDirective } from 'ng2-charts';

@Component({
  selector: 'app-charts',
  imports: [FormsModule, BaseChartDirective],
  templateUrl: './charts.html',
  styleUrl: './charts.css',
})
export class Charts implements OnInit {
  private readonly api = inject(Api);

  protected readonly deviceElements = signal<DeviceElement[]>([]);
  protected readonly selectedIds = signal<Set<string>>(new Set());
  protected readonly hours = signal<number>(24);
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);
  protected readonly lineChartData = signal<ChartData<'line', { x: number; y: number }[]>>({
    datasets: [],
  });

  protected readonly lineChartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: 'time',
        time: { tooltipFormat: 'dd/MM/yyyy HH:mm' },
        ticks: { autoSkip: true, maxRotation: 0 },
      },
    },
  };

  ngOnInit(): void {
    this.api.getDeviceElements().subscribe({
      next: (elements) => this.deviceElements.set(elements),
      error: () => this.error.set('No se han podido cargar los sensores del dispositivo.'),
    });
  }

  toggleSensor(id: string): void {
    const selectedIds = new Set(this.selectedIds());
    if (selectedIds.has(id)) {
      selectedIds.delete(id);
    } else {
      selectedIds.add(id);
    }
    this.selectedIds.set(selectedIds);
  }

  generateChart(): void {
    if (this.selectedIds().size === 0) {
      this.error.set('Selecciona al menos un sensor antes de generar el gráfico.');
      return;
    }

    this.loading.set(true);
    this.error.set(null);

    this.api.getReadingsHistory(this.hours()).subscribe({
      next: (rows) => {
        const datasets = this.deviceElements()
          .filter((element) => this.selectedIds().has(element.id))
          .map((element) => ({
            label: element.name,
            data: rows
              .filter((row) => row[element.id] != null)
              .map((row) => ({
                x: new Date(row.time).getTime(),
                y: row[element.id] as number,
              })),
          }));

        this.lineChartData.set({ datasets });
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se han podido cargar los datos del histórico.');
        this.loading.set(false);
      },
    });
  }

}
