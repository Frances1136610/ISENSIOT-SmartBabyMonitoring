import 'package:flutter/material.dart';
import 'package:smart_babyfoon/Components/Widgets/crying_data.dart';
import 'package:smart_babyfoon/Components/Widgets/environment_data.dart';
import 'package:smart_babyfoon/Components/Widgets/health_data.dart';
import 'package:smart_babyfoon/Components/Widgets/presence_data.dart';


class DataCards extends StatefulWidget {
  const DataCards({super.key});

  @override
  DataCardsState createState() => DataCardsState();
}

class DataCardsState extends State<DataCards> {

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Column(
        children: [
          Expanded(
              child: SizedBox(
                  height: 200,
                  child: PresenceData()
              )
          ),
          Row(
            children: [
              Expanded(
                flex: 7,
                child: SizedBox(
                  height: 150,
                  child: CryingData(),
                )
              ),
              Expanded(
                flex: 3,
                child: SizedBox(
                    height:150,
                    child: EnvironmentData()
                )
              ),
            ],
          ),
          Expanded(
              child: SizedBox(
                height: 200,
                  child: HealthData()
              )
          ),
        ],
      ),
    );
  }
}