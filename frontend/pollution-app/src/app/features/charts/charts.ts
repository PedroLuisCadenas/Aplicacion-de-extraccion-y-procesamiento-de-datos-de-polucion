import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { ChartConfiguration, ChartData } from 'chart.js';
import 'chartjs-adapter-date-fns';
import { Api, DeviceElement, ReadingsHistoryParams } from '../../core/api';
import { FormsModule } from '@angular/forms';
import { BaseChartDirective } from 'ng2-charts';

type RangeMode = 'hours' | 'range';

interface SensorStat {
  id: string;
  label: string;
  avg: number;
  min: number;
  max: number;
}

function round2(value: number): number {
  return Math.round(value * 100) / 100;
}

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
  protected readonly mode = signal<RangeMode>('hours');
  protected readonly hours = signal<number>(24);
  protected readonly rangeStart = signal<string>('');
  protected readonly rangeEnd = signal<string>('');
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);
  protected readonly lineChartData = signal<ChartData<'line', { x: number; y: number }[]>>({
    datasets: [],
  });
  protected readonly intervalStats = signal<SensorStat[]>([]);
  protected readonly isPickerOpen = signal(false);
  protected readonly pickerSearch = signal('');
  protected readonly draftSelectedIds = signal<Set<string>>(new Set());

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

  protected readonly selectedSensorChips = computed(() =>
    this.deviceElements().filter((element) => this.selectedIds().has(element.id)),
  );

  protected readonly filteredElements = computed(() => {
    const search = this.pickerSearch().toLowerCase();
    return this.deviceElements().filter((element) => element.name.toLowerCase().includes(search));
  });

  toggleSensor(id: string): void {
    const selectedIds = new Set(this.selectedIds());
    if (selectedIds.has(id)) {
      selectedIds.delete(id);
    } else {
      selectedIds.add(id);
    }
    this.selectedIds.set(selectedIds);
  }

  clearSelection(): void {
    this.selectedIds.set(new Set());
  }

  openPicker(): void {
    this.draftSelectedIds.set(new Set(this.selectedIds()));
    this.isPickerOpen.set(true);
  }

  closePicker(): void {
    this.isPickerOpen.set(false);
  }

  applyPicker(): void {
    this.selectedIds.set(new Set(this.draftSelectedIds()));
    this.isPickerOpen.set(false);
  }

  toggleDraftSensor(id: string): void {
    const draftSelectedIds = new Set(this.draftSelectedIds());
    if (draftSelectedIds.has(id)) {
      draftSelectedIds.delete(id);
    } else {
      draftSelectedIds.add(id);
    }
    this.draftSelectedIds.set(draftSelectedIds);
  }

  generateChart(): void {
    if (this.selectedIds().size === 0) {
      this.error.set('Selecciona al menos un sensor antes de generar el gráfico.');
      return;
    }

    let params: ReadingsHistoryParams;
    if (this.mode() === 'hours') {
      params = { hours: this.hours() };
    } else {
      if (!this.rangeStart()) {
        this.error.set('Indica al menos la fecha/hora de inicio del rango.');
        return;
      }
      params = {
        start: new Date(this.rangeStart()).toISOString(),
        ...(this.rangeEnd() ? { end: new Date(this.rangeEnd()).toISOString() } : {}),
      };
    }

    this.loading.set(true);
    this.error.set(null);

    this.api.getReadingsHistory(params).subscribe({
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

        const stats = this.deviceElements()
          .filter((element) => this.selectedIds().has(element.id))
          .map((element): SensorStat | null => {
            const values = rows
              .filter((row) => row[element.id] != null)
              .map((row) => row[element.id] as number);

            if (values.length === 0) {
              return null;
            }

            const sum = values.reduce((total, value) => total + value, 0);
            return {
              id: element.id,
              label: element.name,
              avg: round2(sum / values.length),
              min: round2(Math.min(...values)),
              max: round2(Math.max(...values)),
            };
          })
          .filter((stat): stat is SensorStat => stat !== null);

        this.lineChartData.set({ datasets });
        this.intervalStats.set(stats);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se han podido cargar los datos del histórico.');
        this.intervalStats.set([]);
        this.loading.set(false);
      },
    });
  }

}
