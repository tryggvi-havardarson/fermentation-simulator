#partur eitt
#vant hoft
import numpy as np

R=8.314 #j*(mol*K)^-1
T_ref=298.15 #K

water_info = {
    "Kh_ref":0.034,
    "H_sol":-19900
}

ethanol_info = {
    "Kh_ref":0.220,
    "H_sol":-10800
}

glucoes_info = {
    "temp_sens_factor":-0.0010, 
    "Ks_ref":0.120
}


def kH(T,k_ref,H_sol):

    kH=k_ref*np.exp((
        H_sol/R
    )*(
        (1/T_ref)-(1/T)
    ))

    return kH



def kH_blend(T,w_water,w_ethanol):

    kH_water=kH(T,water_info["Kh_ref"],water_info["H_sol"])
    kH_ethanol=kH(T,ethanol_info["Kh_ref"],ethanol_info["H_sol"])

    kH_blend=np.exp(
        w_water*np.log(kH_water)+w_ethanol*np.log(kH_ethanol)
    )

    return kH_blend




def Ks(T,Ks_ref,m):

    Ks=Ks_ref+m*(T-T_ref)

    return Ks



def glucose_effect(T,C_glucose,w_water,w_ethanol):

    Ks_value=Ks(T,glucoes_info["Ks_ref"],glucoes_info["temp_sens_factor"])
    kH_blend_value=kH_blend(T,w_water,w_ethanol)

    kH_final=kH_blend_value*10**(Ks_value*C_glucose)

    return kH_final