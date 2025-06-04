import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

class PresenceData extends StatefulWidget {
  const PresenceData({super.key});

  @override
  State<PresenceData> createState() => _PresenceDataState();
}

class _PresenceDataState extends State<PresenceData> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
         Expanded(
           child: StreamBuilder<QuerySnapshot>(
             stream: FirebaseFirestore.instance
                 .collection('presenceState')
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
                var card = value == false ?
                const Card(
                  color: Color(0xfff70059),
                  child: SizedBox(
                    height: 140,
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        Text(
                          "Baby not present!",
                          style: TextStyle(
                              fontSize: 30,
                              color: Colors.white
                          )
                        ),
                        Icon(
                          FontAwesomeIcons.circleExclamation,
                          color: Colors.white,
                          size: 90,
                        )
                      ],
                    ),
                  ),
                ) :
                const Card(
                  color: Color(0xff61ff61),
                  child: SizedBox(
                    height: 140,
                    child: Center(
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            Text(
                              "Baby is present!",
                              style: TextStyle(
                                  fontSize: 30,
                                  color: Colors.white
                              )
                            ),
                            Icon(
                              Icons.crib,
                              color: Colors.white,
                              size: 110,
                            )
                          ],
                        )
                    ),
                  ),
                );
                return card;
             }
           ),
         )
        ],
      ),
    );
  }
}
