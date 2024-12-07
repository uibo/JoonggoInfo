import 'dart:convert';
import 'package:flutter/material.dart';

import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_charts/charts.dart';
import 'package:intl/intl.dart';

import 'common_widget.dart';

class ChartPage extends ConsumerStatefulWidget {
  const ChartPage ({super.key});

  @override
  ChartPageState createState() => ChartPageState();
}
class ChartPageState extends ConsumerState<ChartPage> {
  bool showChart = false;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [ 
        SettingBar(
          onPressedToRefesh: () {ref.read(malProvider.notifier).refresh();}, 
          onPressedToShorChart: 
          () {
            setState(
              () {
                if (!showChart) showChart = true;
              }
            );
          },
        ),
        Expanded(
          child: SingleChildScrollView(
            child: showChart ? const ChartView() : const SizedBox(),
          )
        ),
      ]
    );
  }
}

final malProvider = StateNotifierProvider<MalNotifier, AsyncValue<ChartData>>((ref) => MalNotifier(ref));
class MalNotifier extends StateNotifier<AsyncValue<ChartData>> {
  final Ref ref;
  late Settings settings;

  MalNotifier(this.ref): super(const AsyncValue.loading()) {
    settings = ref.read(settingsProvider);
  }

  Uri creatUrlFromsettings() {
    String status='';
    if (settings.saleStatus.contains(SaleStatus.selling)) status += '0';
    if (settings.saleStatus.contains(SaleStatus.soldout)) status += '1';
    String featureList = '';
    settings.options.forEach(
      (key, value) {
        if (value == true) {featureList += '1';}
        else {featureList += '0';}
      }
    );
    const baseUrl = 'http://127.0.0.1:8000/movingaverageline/';
    final queryParams = {
      'search_date': settings.fromDate + settings.toDate,
      'battery': settings.battery,
      'status': status,
      'feature_list': featureList,
    };
    if (settings.model != 'All') {
      if (settings.model == 'Normal') {queryParams['model'] = settings.product;}
      else {queryParams['model'] = settings.product + settings.model;}
    }
    if (settings.storage != 'All') {queryParams['storage'] = settings.storage;}
    return Uri.parse(baseUrl).replace(queryParameters: queryParams);
  }

  Future<void> fetchMalData() async {
    state = const AsyncValue.loading();
    try {
    final url = creatUrlFromsettings();
    final res =  await http.get(url);
    state = AsyncValue.data(
      ChartData(
        malMap: jsonDecode(utf8.decode(res.bodyBytes))[0], 
        volumeMap: jsonDecode(utf8.decode(res.bodyBytes))[1],
      )
    );
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  void refresh() {
    settings = ref.read(settingsProvider);
    fetchMalData();
  }
}
class ChartData {
  const ChartData({this.malMap, this.volumeMap});

  final Map? malMap;
  final Map? volumeMap;
}

class SfChartData {
  final DateTime date;
  final int price;
  final int volume;

  const SfChartData ({
    required this.date, 
    required this.price, 
    required this.volume,
  });
}
class ChartView extends ConsumerStatefulWidget {
  const ChartView([Key? key]): super(key: key);

  @override
  ChartViewState createState() => ChartViewState();
}
class ChartViewState extends ConsumerState<ChartView> {
  List<SfChartData> convertlistSfChartData(ChartData chartData) {
    List<SfChartData> listChartData = [];
    var malEntries = chartData.malMap!.entries;
    var volumeEntries = chartData.volumeMap!.entries;
    for (int i = 0; i < malEntries.length; i++) {
      listChartData.add(
        SfChartData(
          date: DateTime.parse(malEntries.elementAt(i).key) ,
          price: malEntries.elementAt(i).value, 
          volume: volumeEntries.elementAt(i).value,
        )
      );
    }
    return listChartData;
  }

  Widget buildChart(List<SfChartData> listSfChartData) {
    return SfCartesianChart(
      legend: const Legend(
        isVisible: true,
        position: LegendPosition.bottom,
      ),
      primaryXAxis: DateTimeAxis(
        intervalType: DateTimeIntervalType.months,
        interval: 1,
        labelRotation: -45,
        dateFormat: DateFormat('yyyy-MM-dd'),
      ),
      primaryYAxis: const NumericAxis(name: 'Price',),
      axes: const [NumericAxis(name: 'Volume', opposedPosition: true,)],
      series: [
        LineSeries<SfChartData, DateTime>(
          dataSource: listSfChartData,
          xValueMapper: (SfChartData data, _) {return data.date;},
          yValueMapper: (SfChartData data, _) {return data.price;},
          yAxisName: 'Price',
          name: 'Price',
        ),
        ColumnSeries<SfChartData, DateTime>(
          dataSource: listSfChartData,
          xValueMapper: (SfChartData data, _) {return data.date;},
          yValueMapper: (SfChartData data, _) {return data.volume;},
          yAxisName: 'Volume',
          name: 'Volume',
        )
      ],
      tooltipBehavior: TooltipBehavior(
        enable: true,
        shared: true,
        activationMode: ActivationMode.singleTap,
      ),
      trackballBehavior: TrackballBehavior(
        enable: true,
        tooltipSettings: const InteractiveTooltip(
          enable: true,
          format: 'point.x : point.y',
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final chartDataValue = ref.watch(malProvider);

    return SizedBox(
    height: 500,
    child: chartDataValue.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stacktrace) => const Text('failed loading data'),
      data: (chartData) => buildChart(convertlistSfChartData(chartData)),
    ),
  );
  }
}