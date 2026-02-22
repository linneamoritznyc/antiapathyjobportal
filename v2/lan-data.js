// Swedish counties (län) & municipalities (kommuner) — 21 län, 290 kommuner
// Source: https://taxonomy.api.jobtechdev.se/v1/taxonomy/specific/concepts/municipality
// Taxonomy IDs used for Platsbanken geographic job filtering.
// Changes extremely rarely — no API dependency needed.
const LAN_DATA = [
    {id:"01",label:"Stockholms län",kommuner:[
        {id:"AvNB_uwa_6n6",label:"Stockholm"},{id:"CCVZ_JA7_d3y",label:"Botkyrka"},{id:"E4CV_a5E_ucX",label:"Danderyd"},
        {id:"magF_Gon_YL2",label:"Ekerö"},{id:"Q7gp_9dT_k2F",label:"Haninge"},{id:"g1Gc_aXK_EKu",label:"Huddinge"},
        {id:"qm5H_jsD_fUF",label:"Järfälla"},{id:"FBbF_mda_TYD",label:"Lidingö"},{id:"aYA7_PpG_BqP",label:"Nacka"},
        {id:"btgf_fS7_sKG",label:"Norrtälje"},{id:"mBKv_q3B_SK8",label:"Nykvarn"},{id:"37UU_T7x_oxG",label:"Nynäshamn"},
        {id:"4KBw_CPU_VQv",label:"Salem"},{id:"8ryy_X54_xJj",label:"Sigtuna"},{id:"Z5Cq_SgB_dsB",label:"Sollentuna"},
        {id:"zHxw_uJZ_NJ8",label:"Solna"},{id:"UTJZ_zHH_mJm",label:"Sundbyberg"},{id:"g6hK_M1o_hiU",label:"Södertälje"},
        {id:"onpA_B5a_zfv",label:"Täby"},{id:"sTPc_k2B_SqV",label:"Tyresö"},{id:"w6yq_CGR_Fiv",label:"Upplands-Bro"},
        {id:"XWKY_c49_5nv",label:"Upplands Väsby"},{id:"K4az_Bm6_hRV",label:"Vallentuna"},{id:"9aAJ_j6L_DST",label:"Vaxholm"},
        {id:"15nx_Vut_GrH",label:"Värmdö"},{id:"8gKt_ZsV_PGj",label:"Österåker"}
    ]},
    {id:"03",label:"Uppsala län",kommuner:[
        {id:"HGwg_unG_TsG",label:"Enköping"},{id:"sD2e_1Tr_4WZ",label:"Heby"},{id:"Bbs5_JUs_Qh5",label:"Håbo"},
        {id:"KALq_sG6_VrW",label:"Knivsta"},{id:"K8A2_JBa_e6e",label:"Tierp"},{id:"otaF_bQY_4ZD",label:"Uppsala"},
        {id:"cbyw_9aK_Cni",label:"Älvkarleby"},{id:"VE3L_3Ei_XbG",label:"Östhammar"}
    ]},
    {id:"04",label:"Södermanlands län",kommuner:[
        {id:"kMxr_NiX_YrU",label:"Eskilstuna"},{id:"P8yp_WT9_Bks",label:"Flen"},{id:"os8Y_RUo_U3u",label:"Gnesta"},
        {id:"snx9_qVD_Dr1",label:"Katrineholm"},{id:"KzvD_ePV_DKQ",label:"Nyköping"},{id:"72XK_mUU_CAH",label:"Oxelösund"},
        {id:"shnD_RiE_RKL",label:"Strängnäs"},{id:"rjzu_nQn_mCK",label:"Trosa"},{id:"rut9_f5W_kTX",label:"Vingåker"}
    ]},
    {id:"05",label:"Östergötlands län",kommuner:[
        {id:"e5LB_m9V_TnT",label:"Boxholm"},{id:"dMFe_J6W_iJv",label:"Finspång"},{id:"U4XJ_hYF_FBA",label:"Kinda"},
        {id:"bm2x_1mr_Qhx",label:"Linköping"},{id:"stqv_JGB_x8A",label:"Mjölby"},{id:"E1MC_1uG_phm",label:"Motala"},
        {id:"SYty_Yho_JAF",label:"Norrköping"},{id:"Pcv9_yYh_Uw8",label:"Söderköping"},{id:"VcCU_Y86_eKU",label:"Vadstena"},
        {id:"Sb3D_iGB_aXu",label:"Valdemarsvik"},{id:"vRRz_nLT_vYv",label:"Ydre"},{id:"bFWo_FRJ_x2T",label:"Åtvidaberg"},
        {id:"Fu8g_29u_3xF",label:"Ödeshög"}
    ]},
    {id:"06",label:"Jönköpings län",kommuner:[
        {id:"y9HE_XD7_WaD",label:"Aneby"},{id:"VacK_WF6_XVg",label:"Eksjö"},{id:"cNQx_Yqi_83Q",label:"Gislaved"},
        {id:"91VR_Hxi_GN4",label:"Gnosjö"},{id:"9zQB_3vU_BQA",label:"Habo"},{id:"KURg_KJF_Lwc",label:"Jönköping"},
        {id:"smXg_BXp_jTW",label:"Mullsjö"},{id:"KfXT_ySA_do2",label:"Nässjö"},{id:"L1cX_MjM_y8W",label:"Sävsjö"},
        {id:"Namm_SpC_RPG",label:"Tranås"},{id:"zFup_umX_LVv",label:"Vaggeryd"},{id:"xJqx_SLC_415",label:"Vetlanda"},
        {id:"6bS8_fzf_xpW",label:"Värnamo"}
    ]},
    {id:"07",label:"Kronobergs län",kommuner:[
        {id:"MMph_wmN_esc",label:"Alvesta"},{id:"GzKo_S48_QCm",label:"Ljungby"},{id:"nXZy_1Jd_D8X",label:"Lessebo"},
        {id:"ZhVf_yL5_Q5g",label:"Markaryd"},{id:"qz8Q_kDz_N2Y",label:"Tingsryd"},{id:"78cu_S5T_Pgp",label:"Uppvidinge"},
        {id:"mmot_H3A_auW",label:"Växjö"},{id:"EK6X_wZq_CQ8",label:"Älmhult"}
    ]},
    {id:"08",label:"Kalmar län",kommuner:[
        {id:"LY9i_qNL_kXf",label:"Borgholm"},{id:"1koj_6Bg_8K6",label:"Emmaboda"},{id:"AEQD_1RT_vM9",label:"Hultsfred"},
        {id:"WPDh_pMr_RLZ",label:"Högsby"},{id:"Pnmg_SgP_uHQ",label:"Kalmar"},{id:"8eEp_iz4_cNN",label:"Mönsterås"},
        {id:"Muim_EAi_EFp",label:"Mörbylånga"},{id:"xk68_bJa_6Fh",label:"Nybro"},{id:"tUP8_hRE_NcF",label:"Oskarshamn"},
        {id:"wYFb_q7w_Nnh",label:"Torsås"},{id:"a7hJ_zwv_2FR",label:"Vimmerby"},{id:"t7H4_S2P_3Fw",label:"Västervik"}
    ]},
    {id:"09",label:"Gotlands län",kommuner:[
        {id:"Ft9P_E8F_VLJ",label:"Gotland"}
    ]},
    {id:"10",label:"Blekinge län",kommuner:[
        {id:"HtGW_WgR_dpE",label:"Karlshamn"},{id:"YSt4_bAa_ccs",label:"Karlskrona"},{id:"1gEC_kvM_TXK",label:"Olofström"},
        {id:"vH8x_gVz_z7R",label:"Ronneby"},{id:"EVPy_phD_8Vf",label:"Sölvesborg"}
    ]},
    {id:"12",label:"Skåne län",kommuner:[
        {id:"waQp_FjW_qhF",label:"Bjuv"},{id:"WMNK_PXa_Khm",label:"Bromölla"},{id:"64g5_Lio_aMU",label:"Burlöv"},
        {id:"gfCw_egj_1M4",label:"Eslöv"},{id:"qj3q_oXH_MGR",label:"Helsingborg"},{id:"autr_KMa_cfp",label:"Hörby"},
        {id:"N29z_AqQ_Ppc",label:"Höör"},{id:"bP5q_53x_aqJ",label:"Hässleholm"},{id:"8QQ6_e95_a1d",label:"Höganäs"},
        {id:"JARU_FAY_hTS",label:"Klippan"},{id:"vrvW_sr8_1en",label:"Kristianstad"},{id:"5ohg_WJU_Ktn",label:"Kävlinge"},
        {id:"Yt5s_Vf9_rds",label:"Landskrona"},{id:"naG4_AUS_z2v",label:"Lomma"},{id:"muSY_tsR_vDZ",label:"Lund"},
        {id:"oYPt_yRA_Smm",label:"Malmö"},{id:"najS_Lvy_mDD",label:"Osby"},{id:"BN7r_iPV_F9p",label:"Perstorp"},
        {id:"dLxo_EpC_oPe",label:"Simrishamn"},{id:"P3Cs_1ZP_9XB",label:"Sjöbo"},{id:"oezL_78x_r89",label:"Skurup"},
        {id:"vBrj_bov_KEX",label:"Staffanstorp"},{id:"2r6J_g2w_qp5",label:"Svalöv"},{id:"n6r4_fjK_kRr",label:"Svedala"},
        {id:"UMev_wGs_9bg",label:"Tomelilla"},{id:"STvk_dra_M1X",label:"Trelleborg"},{id:"Tcog_5sH_b46",label:"Vellinge"},
        {id:"hdYk_hnP_uju",label:"Ystad"},{id:"pCuv_P5A_9oh",label:"Ängelholm"},{id:"tEv6_ktG_QQb",label:"Åstorp"},
        {id:"nBTS_Nge_dVH",label:"Örkelljunga"},{id:"LTt7_CGG_RUf",label:"Östra Göinge"},{id:"i8vK_odq_6ar",label:"Båstad"}
    ]},
    {id:"13",label:"Hallands län",kommuner:[
        {id:"qaJg_wMR_C8T",label:"Falkenberg"},{id:"kUQB_KdK_kAh",label:"Halmstad"},{id:"3XMe_nGt_RcU",label:"Hylte"},
        {id:"3JKV_KSK_x6z",label:"Kungsbacka"},{id:"c1iL_rqh_Zja",label:"Laholm"},{id:"AkUx_yAq_kGr",label:"Varberg"}
    ]},
    {id:"14",label:"Västra Götalands län",kommuner:[
        {id:"17Ug_Btv_mBr",label:"Ale"},{id:"UQ75_1eU_jaC",label:"Alingsås"},{id:"hejM_Jct_XJk",label:"Bengtsfors"},
        {id:"ypAQ_vTD_KLU",label:"Bollebygd"},{id:"TpRZ_bFL_jhL",label:"Borås"},{id:"NMc9_oEm_yxy",label:"Dals-Ed"},
        {id:"ZzEA_2Fg_Pt2",label:"Essunga"},{id:"ZySF_gif_zE4",label:"Falköping"},{id:"kCHb_icw_W5E",label:"Färgelanda"},
        {id:"txzq_PQY_FGi",label:"Götene"},{id:"PVZL_BQT_XtL",label:"Göteborg"},{id:"ZNZy_Hh5_gSW",label:"Grästorp"},
        {id:"roiB_uVV_4Cj",label:"Gullspång"},{id:"J116_VFs_cg6",label:"Herrljunga"},{id:"YbFS_34r_K2v",label:"Hjo"},
        {id:"dzWW_R3G_6Eh",label:"Härryda"},{id:"e413_94L_hdh",label:"Karlsborg"},{id:"ZkZf_HbK_Mcr",label:"Kungälv"},
        {id:"yHV7_2Y6_zQx",label:"Lerum"},{id:"FN1Y_asc_D8y",label:"Lidköping"},{id:"YQcE_SNB_Tv3",label:"Lilla Edet"},
        {id:"z2cX_rjC_zFo",label:"Lysekil"},{id:"7HAb_9or_eFM",label:"Mark"},{id:"Lzpu_thX_Wpa",label:"Mariestad"},
        {id:"tt1B_7rH_vhG",label:"Mellerud"},{id:"96Dh_3sQ_RFb",label:"Munkedal"},{id:"mc45_ki9_Bv3",label:"Mölndal"},
        {id:"tmAp_ykH_N6k",label:"Orust"},{id:"CCiR_sXa_BVW",label:"Partille"},{id:"k1SK_gxg_dW4",label:"Skara"},
        {id:"fqAy_4ji_Lz2",label:"Skövde"},{id:"aKkp_sEX_cVM",label:"Sotenäs"},{id:"wHrG_FBH_hoD",label:"Stenungsund"},
        {id:"PAxT_FLT_3Kq",label:"Strömstad"},{id:"rZWC_pXf_ySZ",label:"Svenljunga"},{id:"qffn_qY4_DLk",label:"Tanum"},
        {id:"aLFZ_NHw_atB",label:"Tibro"},{id:"Zsf5_vpP_Bs4",label:"Tidaholm"},{id:"TbL3_HmF_gnx",label:"Tjörn"},
        {id:"SEje_LdC_9qN",label:"Tranemo"},{id:"CSy8_41F_YvX",label:"Trollhättan"},{id:"a15F_gAH_pn6",label:"Töreboda"},
        {id:"xQc2_SzA_rHK",label:"Uddevalla"},{id:"an4a_8t2_Zpd",label:"Ulricehamn"},{id:"fbHM_yhA_BqS",label:"Vara"},
        {id:"THif_q6H_MjG",label:"Vänersborg"},{id:"NfFx_5jj_ogg",label:"Vårgårda"},{id:"Zjiv_rhk_oJK",label:"Öckerö"},
        {id:"M1UC_Cnf_r7g",label:"Åmål"}
    ]},
    {id:"17",label:"Värmlands län",kommuner:[
        {id:"yGue_F32_wev",label:"Arvika"},{id:"N5HQ_hfp_7Rm",label:"Eda"},{id:"UXir_vKD_FuW",label:"Filipstad"},
        {id:"xnEt_JN3_GkA",label:"Forshaga"},{id:"PSNt_P95_x6q",label:"Grums"},{id:"qk9a_g5U_sAH",label:"Hagfors"},
        {id:"x5qW_BXr_aut",label:"Hammarö"},{id:"hRDj_PoV_sFU",label:"Karlstad"},{id:"ocMw_Rz5_B1L",label:"Kil"},
        {id:"SVQS_uwJ_m2B",label:"Kristinehamn"},{id:"x73h_7rW_mXN",label:"Munkfors"},{id:"mPt5_3QD_LTM",label:"Storfors"},
        {id:"oqNH_cnJ_Tdi",label:"Sunne"},{id:"wmxQ_Guc_dsy",label:"Säffle"},{id:"hQdb_zn9_Sok",label:"Torsby"},
        {id:"ymBu_aFc_QJA",label:"Årjäng"}
    ]},
    {id:"18",label:"Örebro län",kommuner:[
        {id:"dbF7_Ecz_CWF",label:"Askersund"},{id:"pvzC_muj_rcq",label:"Degerfors"},{id:"Ak9V_rby_yYS",label:"Hallsberg"},
        {id:"sCbY_r36_xhs",label:"Hällefors"},{id:"wgJm_upX_z5W",label:"Karlskoga"},{id:"viCA_36P_pQp",label:"Kumla"},
        {id:"oYEQ_m8Q_unY",label:"Laxå"},{id:"yaHU_E7z_YnE",label:"Lekeberg"},{id:"JQE9_189_Ska",label:"Lindesberg"},
        {id:"eF2n_714_hSU",label:"Ljusnarsberg"},{id:"WFXN_hsU_gmx",label:"Nora"},{id:"kuMn_feU_hXx",label:"Örebro"}
    ]},
    {id:"19",label:"Västmanlands län",kommuner:[
        {id:"Jkyb_5MQ_7pB",label:"Arboga"},{id:"7D9G_yrX_AGJ",label:"Fagersta"},{id:"oXYf_HmD_ddE",label:"Hallstahammar"},
        {id:"Fac5_h7a_UoM",label:"Kungsör"},{id:"4Taz_AuG_tSm",label:"Köping"},{id:"jbVe_Cps_vtd",label:"Norberg"},
        {id:"dAen_yTK_tqz",label:"Sala"},{id:"Nufj_vmt_VrH",label:"Skinnskatteberg"},{id:"jfD3_Hdg_UhT",label:"Surahammar"},
        {id:"8deT_FRF_2SP",label:"Västerås"}
    ]},
    {id:"20",label:"Dalarnas län",kommuner:[
        {id:"Szbq_2fg_ydQ",label:"Avesta"},{id:"cpya_jJg_pGp",label:"Borlänge"},{id:"N1wJ_Cuu_7Cs",label:"Falun"},
        {id:"Nn7p_W3Z_y68",label:"Gagnef"},{id:"DE9u_V4K_Z1S",label:"Hedemora"},{id:"7Zsu_ant_gcn",label:"Leksand"},
        {id:"Ny2b_2bo_7EL",label:"Ludvika"},{id:"FPCd_poj_3tq",label:"Malung-Sälen"},{id:"UGcC_kYx_fTs",label:"Mora"},
        {id:"CRyF_5Jg_4ht",label:"Orsa"},{id:"Jy3D_2ux_dg8",label:"Rättvik"},{id:"5zZX_8FH_Sbq",label:"Smedjebacken"},
        {id:"c3Zx_jBf_CqF",label:"Säter"},{id:"4eS9_HX1_M7V",label:"Vansbro"},{id:"cZtt_qGo_oBr",label:"Älvdalen"}
    ]},
    {id:"21",label:"Gävleborgs län",kommuner:[
        {id:"KxjG_ig5_exF",label:"Bollnäs"},{id:"qk8Y_2b6_82D",label:"Gävle"},{id:"yuNd_3bg_ttc",label:"Hofors"},
        {id:"Utks_mwF_axY",label:"Hudiksvall"},{id:"63iQ_V6F_REB",label:"Ljusdal"},{id:"fFeF_RCz_Tm5",label:"Nordanstig"},
        {id:"GEvW_wKy_A9H",label:"Ockelbo"},{id:"JPSe_mUQ_NDs",label:"Ovanåker"},{id:"BbdN_xLB_k6s",label:"Sandviken"},
        {id:"JauG_nz5_7mu",label:"Söderhamn"}
    ]},
    {id:"22",label:"Västernorrlands län",kommuner:[
        {id:"uYRx_AdM_r4A",label:"Härnösand"},{id:"yR8g_7Jz_HBZ",label:"Kramfors"},{id:"v5y4_YPe_TMZ",label:"Sollefteå"},
        {id:"dJbx_FWY_tK6",label:"Sundsvall"},{id:"oJ8D_rq6_kjt",label:"Timrå"},{id:"zBmE_n6s_MnQ",label:"Örnsköldsvik"},
        {id:"swVa_cyS_EMN",label:"Ånge"}
    ]},
    {id:"23",label:"Jämtlands län",kommuner:[
        {id:"gRNJ_hVW_Gpg",label:"Berg"},{id:"eNSc_Nj1_CDP",label:"Bräcke"},{id:"j35Q_VKL_NiM",label:"Härjedalen"},
        {id:"yurW_aLE_4ga",label:"Krokom"},{id:"ppjq_Eci_Wz9",label:"Strömsund"},{id:"Vt7P_856_WZS",label:"Östersund"},
        {id:"D7ax_CXP_6r1",label:"Åre"},{id:"Voto_egJ_FZP",label:"Ragunda"}
    ]},
    {id:"24",label:"Västerbottens län",kommuner:[
        {id:"vQkf_tw2_CmR",label:"Bjurholm"},{id:"tSkf_Tbn_rHk",label:"Dorotea"},{id:"7rpN_naz_3Uz",label:"Lycksele"},
        {id:"7sHJ_YCE_5Zv",label:"Malå"},{id:"wMab_4Zs_wpM",label:"Nordmaling"},{id:"XmpG_vPQ_K7T",label:"Norsjö"},
        {id:"p8Mv_377_bxp",label:"Robertsfors"},{id:"kicB_LgH_2Dk",label:"Skellefteå"},{id:"VM7L_yJK_Doo",label:"Sorsele"},
        {id:"gQgT_BAk_fMu",label:"Storuman"},{id:"QiGt_BLu_amP",label:"Umeå"},{id:"tUnW_mFo_Hvi",label:"Vilhelmina"},
        {id:"izT6_zWu_tta",label:"Vindeln"},{id:"utQc_6xq_Dfm",label:"Vännäs"},{id:"xLdL_tMA_JJv",label:"Åsele"}
    ]},
    {id:"25",label:"Norrbottens län",kommuner:[
        {id:"vkQW_GB6_MNk",label:"Arjeplog"},{id:"A5WX_XVo_Zt6",label:"Arvidsjaur"},{id:"y4NQ_tnB_eVd",label:"Boden"},
        {id:"6R2u_zkb_uoS",label:"Gällivare"},{id:"tfRE_hXa_eq7",label:"Haparanda"},{id:"mp6j_2b6_1bz",label:"Jokkmokk"},
        {id:"cUyN_C9V_HLU",label:"Kalix"},{id:"biN6_UiL_Qob",label:"Kiruna"},{id:"CXbY_gui_14v",label:"Luleå"},
        {id:"dHMF_72G_4NM",label:"Pajala"},{id:"umej_bP2_PpK",label:"Piteå"},{id:"14WF_zh1_W3y",label:"Älvsbyn"},
        {id:"n5Sq_xxo_QWL",label:"Överkalix"},{id:"ehMP_onv_Chk",label:"Övertorneå"}
    ]}
];
