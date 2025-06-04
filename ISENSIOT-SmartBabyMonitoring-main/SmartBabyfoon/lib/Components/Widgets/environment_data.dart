import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';

class EnvironmentData extends StatefulWidget {
  const EnvironmentData({super.key});

  @override
  EnvironmentDataState createState() => EnvironmentDataState();
}

class EnvironmentDataState extends State<EnvironmentData> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          Expanded(
            child: Row(
              children: [
                Expanded(
                  child: StreamBuilder<QuerySnapshot>(
                      stream: FirebaseFirestore.instance
                          .collection('dht22Temp')
                          .orderBy('timestamp', descending: true)
                          .limit(1)
                          .snapshots(),
                      builder: (context, snapshot) {
                        if (snapshot.connectionState == ConnectionState.waiting) {
                          return const Center(child: CircularProgressIndicator());
                        }
                        if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
                          return const Center(child: Text("No Data"));
                        }
                        var document = snapshot.data!.docs.first;
                        var value = document['value'];
                        var cardColor = value < 22
                            ? const Color(0xffc0c4d7)
                            : (value > 24
                            ? const Color(0xfff70059)
                            : const Color(0xfff79400));
                        value = value.toStringAsFixed(1);

                        return Card(
                        color: cardColor,
                        child: SizedBox(
                          height: 75,
                          child: Column(
                            children: [
                              const Text(
                                "Room Temperature",
                                style: TextStyle(
                                  fontSize: 9,
                                  color: Colors.white,
                                ),
                                textAlign: TextAlign.center,
                              ),
                              Text(
                                "$value\u2103",
                                style: const TextStyle(
                                  fontSize: 35,
                                  color: Colors.white,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        ),
                      );
                    }
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: Row(
              children: [
                Expanded(
                  child: StreamBuilder<QuerySnapshot>(
                    stream: FirebaseFirestore.instance
                        .collection('tvoc')
                        .orderBy('timestamp', descending: true)
                        .limit(1)
                        .snapshots(),
                    builder: (context, snapshot) {
                      if (snapshot.connectionState == ConnectionState.waiting) {
                        return const Center(child: CircularProgressIndicator());
                      }
                      if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
                        return const Center(child: Text("No Data"));
                      }
                      var document = snapshot.data!.docs.first;
                      var value = document['value'];
                      var airQuality = value < 400 ? 'Good' : 'Bad';
                      var cardColor = value < 400 ? const Color(0xffc0c4d7) : const Color(0xfff70059);

                      return Card(
                        color: cardColor,
                        child: SizedBox(
                          height: 75,
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Text(
                                "Air Quality",
                                style: TextStyle(
                                  fontSize: 9,
                                  color: Colors.white,
                                ),
                                textAlign: TextAlign.center,
                              ),
                              Text(
                                airQuality,
                                style: const TextStyle(
                                  fontSize: 30,
                                  color: Colors.white,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
